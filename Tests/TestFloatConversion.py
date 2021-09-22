#************
# Imports
#************
import unittest
import TestContext
from TestContext import CSVtoQIF

class TestFloatConversion(unittest.TestCase):
    """ Unit test class to test the text to floating point conversion routine """

    # String to convert, expected float value conversion, float value when forced positive
    __mListFloatConversions = [ 
        ["45.23",       45.23],
        ["$45.23",      45.23],

        ["-45.23",      -45.23],
        ["-$45.23",     -45.23],
        ["($45.23)",    -45.23],

        ["45",          45.0],
        ["$45",         45.0],

        ["-45",         -45.0],
        ["-$45",        -45.00],
        ["($45)",       -45.0],

        [".23",         0.23],
        ["$.23",        0.23],

        ["-.23",        -0.23],
        ["-$.23",       -0.23],
        ["($.23)",      -0.23]
        ]

    def test_ConversionFunction(self) -> None:
        """ Iterates the list of floating point conversion strings to test the conversion function
        
        Parameters
        ----------
        None

        Returns
        -------
        None

        Description
        -----------
        Each test string is passed twice to the conversion function.  The first time we expect the floating
        point value to be returned as in the string.  The second time we expect an absolute value with the
        forcePositive argument set True.
        """
        for testCase in self.__mListFloatConversions:
            msg = "Test string = '{}'".format(testCase[0])
            self.assertEqual(CSVtoQIF._csvFloatToQuickenFloat(testCase[0]), testCase[1], msg)
            self.assertEqual(CSVtoQIF._csvFloatToQuickenFloat(testCase[0], True), abs(testCase[1]), msg)
        return
