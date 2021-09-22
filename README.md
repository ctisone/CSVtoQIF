# CSVtoQIF

Quicken is popular financial management tool widely supported by many financial institutions via Express Web Connect/Direct Connect/Web Connect.  In the cases where direct integration is not supported, financial institutions usually support the download of Web Connect (.QFX) or Quicken Interchange Format (.QIF) files for import into Quicken.  The few remaining institutions that support none of the above will typically support CSV file download.  While helpful, these files cannot be imported into Quicken, greatly reducing their usefulness.

This program was created to convert CSV files into one or more QIF files that can be imported into Quicken.  While the project was intended for the Linux OS, the main program is written under Python 3.9, allowing it to be ported elsewhere.

At the time of this writing, Wikipedia had a good overall description of the QIF file format: https://en.wikipedia.org/wiki/Quicken_Interchange_Format

## Environment

The project was created in the following environment:

- Python 3.9.9
- PyInstaller (pip install PyInstaller)
- Make

## Usage

```bash
CSVtoQIF [-h] [-v] csvFile cfgFile
```

|Target|Type|Description|
|-----|-----|-----|
|-h, --help|Optional|Displays the help message and exits|
|-v|Optional|Displays the program version and exits|
|csvFile|Mandatory|Specifies the CSV input file|
|cfgFile|Mandatory|Specifies the conversion configuration JSON file|

## Configuration JSON File

The conversion process is guided by a JSON configuration file describing the CSV file format and rules for emitting individual records into one or more output QIF files.  The Source directory has a sample configuration JSON file that can be filled out.

### *csvFile* Object

The *csvFile* object is a top level JSON object containing other JSON objects with CSV file details.

```json
"csvFile": {
    "headerRowMap": {
        ...
        ...
    },
    "actionCodeMap": {
        ...
        ...
    }
}
```

### *headerRowMap* Object

The *headerRowMap* tells the program how to map CSV column data to QIF record fields.  Each name/value pair in this object functions as follows:

- ***JSON Name***: The name portion of the pair describes the QIF record field needed by the program when creating QIF records.  This text ***must*** not be changed.
- ***JSON Value***: The value portion of the pair is the CSV file header name corresponding to the QIF record field.

Every object name/value pair must be filled out, and the CSV file is allowed to have columns above and beyond what is listed here.

In the example below, the CSV column titled "Fund Name" represents data populated into QIF "Security" fields.

```json
"headerRowMap": {
    "dateColumn": "Date",
    "actionColumn": "Action",
    "securityColumn": "Fund Name",
    "priceColumn": "Price",
    "quantityColumn": "Quantity",
    "valueColumn": "Amount",
    "memoColumn": "Transaction Type"
}
```

### *actionCodeMap* Object

The *actionCodeMap* tells the program how to map transaction types found in the CSV file to Quicken compatible QIF action field codes.  The transaction types are found in the CSV files within the column described by the *headerRowMap* object *actionColumn* value above.  (e.g. For the example above, this would be the CSV file "Action" column.)

- ***JSON Name***: The name portion of the pair describes the QIF action fields that can be emitted into QIF records.  This text ***must*** not be changed as it represents data recognized by Quicken.
- ***JSON Value***: The value portion of the pair is the CSV record action corresponding to the QIF action field.

In the example below, a CSV file transaction type of "Buy" is mapped to a QIF action field value of "ShrsIn".  Note that only the values expected to be found in the CSV need be populated.

```json
"actionCodeMap": {
    "Buy": "",
    "BuyX": "",
    "Sell": "",
    "SellX": "",

    ...
    ...
    ...

    "RtrnCap": "",
    "RtrnCapX": "",
    "StkSplit": "",
    "ShrsOut": "Sell",
    "ShrsIn": "Buy"
}
```

### *qifFiles* Array

*qifFiles* is an array of one or more objects that tells the program how to steer QIF output record data.

The program supports multiple files, and each file is imported into a single Quicken account.  This can be useful for users using multiple Quicken accounts to track transactions in a single online account.  This might be the case, for example, where the online account is a Roth 401k and two Quicken accounts have been setup to differentiate between already taxed employee contributions and untaxed employer matching funds.  When there are multiple potential files, they are tested in the order listed with the first match receiving the record.

It is an error if all records are not mapped to a file.  If for some reason certain CSV file records are not desired in the output, they can be filtered out by steering them to a dummy QIF file.

- ***name***: The name of the QIF output file to receive transaction data.
- ***matchColumn***: The native CSV file column name used to determine a match.
- ***matchRegEx***: A RegEx expression used to test the *matchColumn* data and determine if a match exists.

In the example below, any record containing the word "Roth" in the CSV file "Category" field is mapped to the Roth.qif output file.  Records containing the phrase "Safe Harbor Match" in the CSV file "Category" field are mapped to the SafeHarbor.qif output file.

```json
"qifFiles": [
    {
        "name": "Roth.qif",
        "matchColumn": "Category",
        "matchRegEx": "Roth"
    },
    {
        "name": "SafeHarbor.qif",
        "matchColumn": "Category",
        "matchRegEx": "Safe Harbor Match"
    }
]
```

## Makefile Targets

The following targets are supported by the project Makefile:

|Target|Description|
|-----|-----|
|all|Builds the final executable as a standalone executable|
|variables|Provides a diagnostic dump of all internal Makefile variables|
|install|Installs the final executable in the deploy directory|
|uninstall|Removes the final executable from the deploy directory|
|installdirs|Creates the deploy directory as required|
|clean|Cleans the project directory structure of all build artifacts|
|check|Runs unit tests|

## Revision History

|Version|Description|
|-----|-----|
|1.0.0|Initial release|
