import os
import directory_manager

manager = directory_manager.DirectoryManager(
        os.path.join(os.path.expanduser('~'), 'tmp/crojudge'))
manager.build_from_spreadsheet()
