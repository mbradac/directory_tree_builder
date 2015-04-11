from __future__ import print_function
import os
import sys
import unicodedata
import _settings
from spreadsheet_parser import data_manager
from PyPDF2 import PdfFileWriter, PdfFileReader

def _makedirs(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

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
        _makedirs(self.__tmp_dir)
        for task in tasks:
            path = self.task_path(task)
            try:
                _makedirs(path)
                self.__save_task_pdf(task)
            except:
                print("Failed to download task: " + task.key(), file=sys.stderr)

    def task_path(self, task):
        contest = self.__data_manager.contest_of_task(task)
        num = self.__data_manager.tasks_in_contest(contest).index(task)
        task_folder = ('%02d' % (num + 1)) + '-' + unicodedata.normalize(
                'NFD', task.name).encode('ascii', 'ignore')
        return os.path.join(self.contest_path(contest), task_folder)
    
    def task_pdf_path(self, task):
        return os.path.join(self.task_path(task), 
                task.normalized_name() + '.pdf')

    def contest_path(self, contest):
        return os.path.join(self.__tasks_dir, contest.short_name,
                str(contest.year), contest.round)

    def __save_task_pdf(self, task):
        try:
            tmp_pdf_path = os.path.join(self.__tmp_dir, 
                    task.key() + '.pdf')
            task.download_text_pdf(tmp_pdf_path)
            with open(tmp_pdf_path, 'rb') as input_stream:
                input_pdf = PdfFileReader(input_stream)
                if input_pdf.isEncrypted:
                    input_pdf.decrypt('')
                output_pdf = PdfFileWriter()
                for page in task.pages:
                    output_pdf.addPage(input_pdf.getPage(page-1))
                with open(self.task_pdf_path(task), 'wb') as output_stream:
                    output_pdf.write(output_stream)
        finally:
            os.remove(tmp_pdf_path)
