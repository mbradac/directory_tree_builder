import os
import unicodedata
import _settings
from spreadsheet_parser import data_manager

class DirecoryManager(object):
    def __init__(self, root):
        super(DirecoryManager, self).__init__()
        self.__makedirs(_settings.TMP)
        self.__root = root
        self.__makedirs(root)
        self.__data_manager = data_manager.DataManager()
        self.__contests = None

    def build(self):
        self.__tasks = self.__data_manager.get_tasks(False)
        self.__data_manager.get_contests(False) # break cache
        for task in self.__tasks:
            print self.task_path(task)

    def task_path(self, task):
        contest = self.__data_manager.contest_of_task(task)
        num = self.__data_manager.tasks_in_contest(contest).index(task)
        task_folder = ('%02d' % (num + 1)) + '-' + unicodedata.normalize(
                'NFD', task.name).encode('ascii', 'ignore')
        return os.path.join(self.contest_path(contest), task_folder)

    def contest_path(self, contest):
        return os.path.join(self.__root, contest.short_name,
                str(contest.year), contest.round)

    def __makedirs(self, path):
        try:
            os.makedirs(_settings.TMP)
        except OSError:
            assert os.path.isdir(_settings.TMP)
