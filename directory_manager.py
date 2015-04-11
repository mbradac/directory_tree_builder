import os
import unicodedata
import _settings
from spreadsheet_parser import data_manager

def _makedirs(path):
    try:
        os.makedirs(_settings.TMP)
    except OSError:
        assert os.path.isdir(_settings.TMP)

class DirectoryManager(object):
    def __init__(self, root):
        super(DirectoryManager, self).__init__()
        self.__root = root
        self.__tmp_dir = os.path.join(root, _settings.TMP)
        self.__tasks_dir = os.path.join(root, _settings.TASKS)
        self.__garbage_dir = os.path.join(root, _settings.GARBAGE)
        self.__checkers_dir = os.path.join(root, _settings.CHECKERS)
        self.__data_manager = data_manager.DataManager()

    def build_from_spreadsheet(self):
        contests = self.__data_manager.get_contests(False)
        tasks = self.__data_manager.get_tasks(False)
        for task in tasks:
            print self.task_path(task)

    def task_path(self, task):
        contest = self.__data_manager.contest_of_task(task)
        num = self.__data_manager.tasks_in_contest(contest).index(task)
        task_folder = ('%02d' % (num + 1)) + '-' + unicodedata.normalize(
                'NFD', task.name).encode('ascii', 'ignore')
        return os.path.join(self.contest_path(contest), task_folder)

    def contest_path(self, contest):
        return os.path.join(self.__tasks_dir, contest.short_name,
                str(contest.year), contest.round)
