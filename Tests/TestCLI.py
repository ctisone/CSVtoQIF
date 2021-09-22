#************
# Imports
#************
import os
import io
import sys
import unittest
import argparse

import TestContext
from TestContext import CSVtoQIF

class TestCLI(unittest.TestCase):
    """ Unit test class to test the CLI interface """

    __mArg1 = "CsvFileName"
    __mArg2 = "ConfigFileName"
    

    def setUp(self) -> None:
        """ Setup method to redirect stdout and stderr to a Null stream to avoid argparse printing """
        self.__mNullStream = open(os.devnull, 'w')
        sys.stdout = self.__mNullStream
        sys.stderr = self.__mNullStream
        super().setUp()
        return

    def tearDown(self) -> None:
        """ Tear down method to restore stdout and stdin to their original values """
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.__mNullStream.close()
        super().tearDown()
        return

    def test_NoPositionalArgs(self):
        """ Tests the CLI parser by passing no arguments """

        with self.assertRaises(SystemExit):
            CSVtoQIF._parseCommandLine([])
        return

    def test_OnePositionalArg(self):
        """ Tests the CLI parser by passing a single argument """

        with self.assertRaises(SystemExit):
            CSVtoQIF._parseCommandLine([ self.__mArg1 ])
        return

    def test_TwoPositionalArg(self):
        """ Tests the CLI parser by passing the two required positional arguments """

        try:
            cliNamesSpace = CSVtoQIF._parseCommandLine([ self.__mArg1, self.__mArg2 ])
            self.assertEqual(cliNamesSpace.csvFile, self.__mArg1)
            self.assertEqual(cliNamesSpace.cfgFile, self.__mArg2)
        except BaseException as err:
            self.fail("Unexpected exception of type: '{}'".format(type(err)))
        return

