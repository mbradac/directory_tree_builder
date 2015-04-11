import os
import directory_manager
from spreadsheet_parser.data_manager import DataManager

manager = directory_manager.DirectoryManager(
        os.path.join(os.path.expanduser('~'), 'tmp/crojudge'))
data = DataManager()

c = data.get_contests()[0]

for task in data.tasks_in_contest(c):
    print manager.task_path(task)
