#************
# Imports
#************
import unittest
from TestFloatConversion import TestFloatConversion
from TestCLI import TestCLI
from TestIntegration import TestIntegration

# The TestContext namespace will have imported into it modules from other folders we are testing
from TestContext import CSVtoQIF

if __name__ == "__main__":
    unittest.main()
