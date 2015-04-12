import os
import directory_manager

manager = directory_manager.DirectoryManager(
        os.path.join('/media/mislav/DATA1/crojudge'))
manager.build_from_spreadsheet()
