
#************
# Imports
#************
import csv
from genericpath import isfile
import json
import re
import argparse
import os
import sys
from typing import List

#******************
# Constants/Enums
#******************
PROGRAM_VERSION = "CSVtoQIF 1.0.0"

# JSON config file object name strings
JSON_OBJECT_INPUT_FILE = "csvFile"
JSON_OBJECT_INPUT_FILE_HEADERS = "headerRowMap"
JSON_OBJECT_INPUT_FILE_ACTIONS = "actionCodeMap"
JSON_OBJECT_OUTPUT_FILES = "qifFiles"

# Key names from the Input File object header object
JSON_KEY_HEADER_DATE = "dateColumn"
JSON_KEY_HEADER_ACTION = "actionColumn"
JSON_KEY_HEADER_SECURITY = "securityColumn"
JSON_KEY_HEADER_PRICE = "priceColumn"
JSON_KEY_HEADER_QUANTITY = "quantityColumn"
JSON_KEY_HEADER_VALUE = "valueColumn"
JSON_KEY_HEADER_MEMO = "memoColumn"

# Key name from the output file objects
JSON_KEY_OUTPUT_FILE_NAME = "name"
JSON_KEY_OUTPUT_FILE_MATCH_COLUMN = "matchColumn"
JSON_KEY_OUTPUT_FILE_MATCH_REGEX = "matchRegEx"
JSON_KEY_OUTPUT_FILE_HANDLE = "__fileHandle"

# Exception strings raised by this file
ERROR_BAD_MONEY_VALUE = "Cannot find monetary value in string '{}'"
ERROR_NO_OUTPUT_FILE = "Cannot map CSV file record to an output file: {}"
ERROR_CSV_FILES_DOES_NOT_EXIST = "CSV file '{}' does not exist"
ERROR_CFG_FILES_DOES_NOT_EXIST = "Config file '{}' does not exist"


#**************
# Main Logic
#**************
def main(CliArgs: list[str] = None) -> None:
    """ Script main() function. 

    Parameters
    ----------
    CliArgs:    CLI arguments exclusive of the Python file name.  This argument is provided to support unit testing, 
                and if not provided, sys.argv values will be used.
    
    Returns
    -------
    None
    """
    print("\n\n***** CSV to QIF File Converter *****\n")

    # If we have been given args, pass them to the CLI parser.  Otherwise use the sys.argv args 
    # past the Python file name.
    argNamespace = _parseCommandLine(sys.argv[1:] if (CliArgs is None) else CliArgs)

    # Check that the files passed to us exist
    if (not os.path.isfile(argNamespace.csvFile)):
        raise Exception(ERROR_CSV_FILES_DOES_NOT_EXIST.format(argNamespace.csvFile))
    if (not os.path.isfile(argNamespace.cfgFile)):
        raise Exception(ERROR_CFG_FILES_DOES_NOT_EXIST.format(argNamespace.cfgFile))

    # Open the config file and extract its JSON contents
    with open(argNamespace.cfgFile, "rt") as cfgFile:
        jsonCfg = json.loads(cfgFile.read())
    jsonHeaderMap = jsonCfg[JSON_OBJECT_INPUT_FILE][JSON_OBJECT_INPUT_FILE_HEADERS]
    jsonActionMap = jsonCfg[JSON_OBJECT_INPUT_FILE][JSON_OBJECT_INPUT_FILE_ACTIONS]
    jsonOutputFiles = jsonCfg[JSON_OBJECT_OUTPUT_FILES]

    # Iterate the output files array and open an output file for each entry
    for fileDesc in jsonOutputFiles:
        fileDesc[JSON_KEY_OUTPUT_FILE_HANDLE] = open(fileDesc[JSON_KEY_OUTPUT_FILE_NAME], "wt")

    # Convert the JSON action code map into a dictionary of Quicken codes (reverse the positions of the key-value pairs).
    # Only non-empty text entries from the JSON file are in the dictionary.  Keys are converted to CAPS to prevent case dependent search failures.
    quickenActionDict = {}
    for quickenAction in jsonActionMap:
        quickenActionDict[jsonActionMap[quickenAction].upper()] = quickenAction
    try:
        quickenActionDict.pop("")   # Get rid of anything mapped to an empty string
    except KeyError:
        # This will happen if there is nothing mapped to an empty string (all actions mapped in the JSON config file)
        pass

    # Open the CSV file and parse it line by line
    recordsProcessed = 0
    with open(argNamespace.csvFile, "rt") as csvFile:
        csvReader = csv.DictReader(csvFile)
        for row in csvReader:
            recordsProcessed = recordsProcessed + 1
            qifRecord = "D{}\nN{}\nY{}\nI{}\nT{:,.2f}\nQ{:,}\nM{}\n^\n".format(
                                    row[jsonHeaderMap[JSON_KEY_HEADER_DATE]],                                    # D
                                    quickenActionDict[row[jsonHeaderMap[JSON_KEY_HEADER_ACTION]].upper()],       # N
                                    row[jsonHeaderMap[JSON_KEY_HEADER_SECURITY]],                                # Y
                                    _csvFloatToQuickenFloat(row[jsonHeaderMap[JSON_KEY_HEADER_PRICE]]),          # I
                                    _csvFloatToQuickenFloat(row[jsonHeaderMap[JSON_KEY_HEADER_VALUE]]),          # T
                                    _csvFloatToQuickenFloat(row[jsonHeaderMap[JSON_KEY_HEADER_QUANTITY]], True), # Q
                                    row[jsonHeaderMap[JSON_KEY_HEADER_MEMO]])                                    # M

            # Iterate the output files and write the string to the first file that matches criteria
            dataWasWritten = False
            for fileDesc in jsonOutputFiles:
                if(not re.match(fileDesc[JSON_KEY_OUTPUT_FILE_MATCH_REGEX], row[fileDesc[JSON_KEY_OUTPUT_FILE_MATCH_COLUMN]]) is None):
                    fileDesc[JSON_KEY_OUTPUT_FILE_HANDLE].write(qifRecord)
                    dataWasWritten = True
                    break

            # Make sure the record went somewhere
            if (not dataWasWritten):
                raise Exception(ERROR_NO_OUTPUT_FILE.format(qifRecord))

    # Clean up
    for fileDesc in jsonOutputFiles:
        fileDesc[JSON_KEY_OUTPUT_FILE_HANDLE].close()
    print("{} CSV records processed".format(recordsProcessed))
    return

def _parseCommandLine(Args: List[str]) -> argparse.Namespace:
    """ Builds and executes the command line parser.
    
    Parameters
    ----------
    Args: A list of strings representing the command line arguments.  This are the args after
        the Python file name in the command line (e.g. sys.argv[1:])

    Returns
    -------
    argparse.Namespace: The namespace object returned from the command line argument parser.
    """
    parser = argparse.ArgumentParser(description = "Converts financial CSV files to the Quicken QIF format")
    parser.version = PROGRAM_VERSION

    # Add positional arguments
    parser.add_argument("csvFile", help = "Specify the input CSV file")
    parser.add_argument("cfgFile", help = "Specify the conversion configuration JSON file")

    # Add optional arguments
    parser.add_argument("-v", action = "version", help = "Shows the version and exits")
    return(parser.parse_args(Args))

def _csvFloatToQuickenFloat(CsvFloatText: str, ForcePositive: bool = False) -> float:
    """ General function to turn a CSV floating point string into a numeric float value. 

    Parameters
    ----------
    CsvFloatText: A CSV string containing a floating point value.
    ForcePositive: When set True, the floating point value will always be returned as a positive value.
    
    Returns
    -------
    float: The floating point value extracted from the string.

    Description
    -----------
    CSV files will contain many strings representing floating point numbers.  These will generally
    represent amounts of currency or shares.  Depending on the CSV file format, the strings may
    contain additional information such as a currency symbol (e.g. $), or if the number is negative,
    a minus sign.  Sometimes accounting formats are used and negative values are found within 
    parenthesis.  This function will find and return the signed floating point number in the string.
    """

    # Somewhere in the money string should be a floating point number.  The string may contain a
    # currency character and a negative sign or be in parenthesis (accounting format) if negative.
    # The regex string looks for a sequence of digits followed by an option decimal point with more
    # digits.  This covers cases when the float value is actually an integer in the string.
    match = re.search("([\d]*\.{0,1}[\d]+)", CsvFloatText)
    if(match == None):
        raise Exception(ERROR_BAD_MONEY_VALUE.format(CsvFloatText))

    # There should be a single match. Convert it to a float.
    value = float(match.group())

    # If the money string has a negative sign or parenthesis in it, make the value negative.  Unless
    # the caller has specified leaving it as a positive number.
    if(not ForcePositive):
        match = re.search("[-()]", CsvFloatText)
        if (match != None):
            value = value * -1.0
    return(value)

if __name__ == "__main__":
    main()
