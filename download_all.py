import sys

from directory_manager import DirectoryManager
manager = DirectoryManager(sys.argv[1])
manager.build_from_spreadsheet()
