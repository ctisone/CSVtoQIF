#************
# Imports
#************
import os
import sys 

# Append the system path to include other directories with modules to be tested, then import those modules.
# Test files can import this module then import the modules imported below.
sys.path.insert(0, os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Source'))))
import CSVtoQIF
