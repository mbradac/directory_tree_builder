import os
import directory_manager

manager = directory_manager.DirectoryManager(
        os.path.join('/home/mislav/tmp/2'))
manager.build_from_spreadsheet(build_tests=False)
