#************
# Imports
#************
import os
import unittest
import json
import csv
import random
import datetime

import TestContext
from TestContext import CSVtoQIF

class TestIntegration(unittest.TestCase):
    """ Integration tests for the entire program
    
        This class will randomize some amount of data into a CSV file that the program will convert across 
        multiple output QIF files.  Those QIF files will be read back in, parsed and checked against the 
        original data.
     """

    # Constants
    _CHECK_MONEY_DECIMAL_PLACES = 2

    # The test files are located in a directory below where this file is kept in the project
    __mTestFileDir = os.path.join(os.path.dirname(__file__), "TestFileDir")
    __mTestConfigFileFullName = os.path.join(__mTestFileDir, "TestConfigFile.json")
    __mTestCsvFileFullName = os.path.join(__mTestFileDir, "TestCsvFile.csv")
    __mTestQifFile1FullName = os.path.join(__mTestFileDir, "RothOutputFile.qif")
    __mTestQifFile2FullName = os.path.join(__mTestFileDir, "401kOutputFile.qif")

    # Data for the CSV file
    __mSecurities = ["Apple", "Google", "Tesla", "Disney", "Netflix" ]
    __mCsvDataList = list()
    __mRecordIdFormat = "Test Record {}"

    # Data for the configuration file
    __mJsonConfigObj = {
        "csvFile":
        {
            "headerRowMap":
            {
                "dateColumn": "CsvDate",
                "actionColumn": "CsvAction",
                "securityColumn": "CsvSecurity",
                "priceColumn": "CsvPrice",
                "quantityColumn": "CsvQuantity",
                "valueColumn": "CsvValue",
                "memoColumn": "CsvMemo"
            },
            "actionCodeMap":
            {
                "Buy": "CsvBuy",
                "BuyX": "CsvBuyX",
                "Sell": "CsvSell",
                "SellX": "CsvSellX",
                "CGLong": "CsvCGLong",
                "CGLongX": "CsvCGLongX",
                "CGMid": "CsvCGMid",
                "CGMidX": "CsvCGMidX",
                "CGShort": "CsvCGShort",
                "CGShortX": "CsvCGShortX",
                "Div": "CsvDiv",
                "DivX": "CsvDivX",
                "IntInc": "CsvIntInc",
                "IntIncX": "CsvIntIncX",
                "ReinvDiv": "CsvReinvdiv",
                "ReinvInt": "CsvReinvInt",
                "ReinvLg": "CsvReinvLg",
                "ReinvMd": "CsvReinvMd",
                "ReinvSh": "CsvReinvSh",
                "Reprice": "CsvReprice",
                "XIn": "CsvXIn",
                "XOut": "CsvXOut",
                "MiscExp": "CsvMiscExp",
                "MiscExpX": "CsvMiscExpX",
                "MiscInc": "CsvMiscInc",
                "MiscIncX": "CsvMiscIncX",
                "MargInt": "CsvMargInt",
                "MargIntX": "CsvMargIntX",
                "RtrnCap": "CsvRtrnCap",
                "RtrnCapX": "CsvRtrnCapX",
                "StkSplit": "CsvStkSplit",
                "ShrsOut": "CsvShrsOut",
                "ShrsIn": "CsvShrsIn"
            }
        },
        "qifFiles":
        [
            {
                "name": __mTestQifFile1FullName,
                "matchColumn": "CsvChooser",
                "matchRegEx": "Roth"
            },
            {
                "name": __mTestQifFile2FullName,
                "matchColumn": "CsvChooser",
                "matchRegEx": "401k"
            }
        ]
    }

    def setUp(self) -> None:
        """ Sets up for the integration tests by assuring an empty test directory resides below the test module """

        # Create the test directory if it doesn't exist, clean it up if it does
        if (os.path.exists(self.__mTestFileDir)):
            self.__cleanTestFileDir()
        else:
            os.makedirs(self.__mTestFileDir)

        # Create a JSON config file and a CSV data file that will be used for all tests
        with open(self.__mTestConfigFileFullName, "wt") as jsonFile:
            json.dump(self.__mJsonConfigObj, jsonFile, indent=3)
        self._createTestCsvFile()

        super().setUp()
        return

    def tearDown(self) -> None:
        """ Tears down the integration test by deleting the test directory and all files """

        # There is a bug in Python where directories we create cannot be deleted in the same session (https://bugs.python.org/issue39327).
        # Normally we would want to delete the folder, but instead just clean it up.
        if (os.path.exists(self.__mTestFileDir)):
            self.__cleanTestFileDir()
        super().tearDown()
        return

    def __cleanTestFileDir(self) -> None:
        """ Removes all files from the test directory """
        
        with os.scandir(self.__mTestFileDir) as files:
            for file in files:
                os.remove(file.path)
        return

    def _createTestCsvFile(self) -> None:
        """ Creates a randomized CSV file for conversion testing """

        # Make a list of all the action codes that can be found in the CSV file.  These will be randomly
        # selected when creating a CSV file.
        actionList = list()
        actionDict = self.__mJsonConfigObj["csvFile"]["actionCodeMap"]
        for key in actionDict:
            actionList.append(actionDict[key])

        # Create the CSV file and write row data to it.  The row data will also be cached locally
        # to more easily verify the output QIF files.
        with open(self.__mTestCsvFileFullName, "wt") as csvFile:
            writer = csv.DictWriter(csvFile,
                                    [   "CsvDate",
                                        "CsvAction",
                                        "CsvSecurity",
                                        "CsvPrice",
                                        "CsvQuantity",
                                        "CsvValue",
                                        "CsvMemo",
                                        "CsvChooser"
                                    ],
                                    extrasaction="ignore"   # Extra fields will be present to facilitate testing
                                    )
            writer.writeheader()

            # Cache some variables
            outputFiles = self.__mJsonConfigObj["qifFiles"]
            startDate = datetime.date(1990, 1, 1)
            endDate = datetime.date(2050, 12, 31)
            numDays = (endDate - startDate).days

            # Generate some randomized row data that is added to a CSV dictionary.  Fields prefixed with
            # "test" are not emitted into the file and are for our use in testing.  For easier comparison
            # later during testing, convert non calculated floating point values to strings.  The floats
            # we calculate can have rounding errors that will be rectified during the comparisons.
            for row in range(100):
                price = random.random() * 1000.0
                quantity = (random.random() * 200.0) - 100.0
                date = startDate + datetime.timedelta(days = random.randrange(numDays))
                self.__mCsvDataList.append({
                    # Field names starting with "Csv" are the mandatory fields corresponding with actual CSV data
                    "CsvDate"       : date.strftime("%-m/%-d/%Y"),
                    "CsvAction"     : random.choice(actionList),
                    "CsvSecurity"   : random.choice(self.__mSecurities),
                    "CsvPrice"      : str(price),
                    "CsvQuantity"   : str(quantity),
                    "CsvValue"      : price * quantity,
                    "CsvMemo"       : self.__mRecordIdFormat.format(row),
                    "CsvChooser"    : outputFiles[random.randint(0, len(outputFiles) - 1)]["matchRegEx"],

                    # Fields starting with "Test" are extra fields used for test purposes
                    "TestDate"      : date.strftime("%Y%m%d"),  # Copy of the date value used for sorting the data after the list is filled
                    "TestCount"     : 0                         # Counts how many times the record shows up in a QIF file
                    })

            # Sort the data in date order and write the rows to the CSV test file
            self.__mCsvDataList.sort(key=lambda row: row["TestDate"])
            writer.writerows(self.__mCsvDataList)
        return

    def _verifyQifFile(self, QifName: str) -> None:
        """ Verifies the named QIF file contents against the original data source.
    
        Parameters
        ----------
        QifName: The fully pathed QIF file name to verify.

        Returns
        -------
        None.

        Description
        -----------
        This function does the preliminary parsing of the QIF file to form a QIF record that is verified by _verifyQifRecord.
        A QIF record spans multiple sequential lines in the QIF file and end with a line containing the caret ('^')
        character.  Each other line contains a single character code describing the individual data point followed
        by numeric data. e.g. I500 signifies 500 shares of stock.
        """

        qifRecord = dict()
        with open(QifName, "rt") as qifFile:
            for line in qifFile:
                if line[0] == "^":
                    self._verifyQifRecord(qifRecord)
                    qifRecord.clear()

                # Do not allow multiple settings of the same key (invalid QIF record)
                if line[0] in qifRecord.keys():
                    raise Exception("Duplicate key '{}' found in file: {}".format(line[0], QifName))
                qifRecord[line[0]] = line[1:].rstrip()
        return

    def _verifyQifRecord(self, QifRecord: dict[str, str]) -> None:
        """  This function verifies the QIF record by first matching it to the original data set via the memo (M)
        field then checking all other data elements.

        Parameters
        ----------
        QifRecord: A dictionary containing the raw keys for a QIF record as extracted from the QIF file.

        Returns
        -------
        None.
        """

        # The CSV test data uses the memo (M) field as a unique record identifier.  Find that record then
        # match all the mandatory values in the parsed QIF record to the CSV test data.  There should
        # be only one match in the list.
        generator = (record for record in self.__mCsvDataList if QifRecord["M"] == record["CsvMemo"])
        matchedRecord = next(generator)
        self.assertRaises(StopIteration, lambda : next(generator))

        # The date (D), security (Y), and price (I) fields should match exactly.  
        # The transaction amount (T) field represents a calculated value and must be checked to some limited number
        # of decimal places after the commas are removed. 
        # The quantity (Q) field is always a positive number in the QIF file even when representing a deduction.
        self.assertEqual(QifRecord["D"], matchedRecord["CsvDate"])
        self.assertEqual(QifRecord["Y"], matchedRecord["CsvSecurity"])
        self.assertEqual(QifRecord["I"], matchedRecord["CsvPrice"])
        self.assertAlmostEqual(float(QifRecord["T"].replace(",", "")), matchedRecord["CsvValue"], self._CHECK_MONEY_DECIMAL_PLACES)
        self.assertEqual(QifRecord["Q"], matchedRecord["CsvQuantity"].replace("-", ""))
        
        # Get the CsvAction from the matched record, do a reverse lookup of the key in the JSON config object and match that
        # to the QIF file action (N) parameter.  Assure that only one record was returned.
        generator = (key for key, value in self.__mJsonConfigObj["csvFile"]["actionCodeMap"].items() if value == matchedRecord["CsvAction"])
        self.assertEqual(QifRecord["N"], next(generator))
        self.assertRaises(StopIteration, lambda : next(generator))

        # Increment the count for this record each time we see it in a QIF file
        matchedRecord["TestCount"] = matchedRecord["TestCount"] + 1
        return

    def test_Conversion(self) -> None:
        """ Invokes main() with the proper CLI args to run a conversion process.
        
        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """

        # Invoke the conversion process.  This will make new QIF files from data source entries
        # written to the CSV file and routed per the JSON config file.
        CSVtoQIF.main([ self.__mTestCsvFileFullName, self.__mTestConfigFileFullName ])

        # Loop over all potential QIF output files to parse the records they contain
        for qifFile in self.__mJsonConfigObj["qifFiles"]:
            self._verifyQifFile(qifFile["name"])

        # Verify that all data source entries made it into a single file.  The search for any data record
        # having a test count != 1 should be empty
        generator = (record for record in self.__mCsvDataList if record["TestCount"] != 1)
        self.assertRaises(StopIteration, lambda : next(generator))
        return
