from __future__ import print_function
import os, sys, fnmatch
import shutil
import unicodedata
import _settings
from spreadsheet_parser import data_manager
from PyPDF2 import PdfFileWriter, PdfFileReader
import zipfile

def _makedirs(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def _extract_as(zfile, name_in_zip, destination_path):
    with zfile.open(name_in_zip) as source_stream:
        with open(destination_path, 'wb') as destination_stream:
            shutil.copyfileobj(source_stream, destination_stream)

class DirectoryManager(object):
    def __init__(self, root):
        super(DirectoryManager, self).__init__()
        self.__root = root
        self.__tmp_dir = os.path.join(root, _settings.TMP)
        self.__tasks_dir = os.path.join(root, _settings.TASKS)
        self.__garbage_dir = os.path.join(root, _settings.GARBAGE)
        self.__checkers_dir = os.path.join(root, _settings.CHECKERS)
        self.__data_manager = data_manager.DataManager()

    def build_from_spreadsheet(self, build_pdfs=True, build_tests=True):
        contests = self.__data_manager.get_contests(False)
        tasks = self.__data_manager.get_tasks(False)
        _makedirs(self.__tmp_dir)
        for task in tasks:
            path = self.task_path(task)
            try:
                _makedirs(path)
                if build_pdfs: 
                    self.__save_task_pdf(task)
                if build_tests:
                    self.__save_task_tests(task)
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
            extension = '.pdf'
            sep = task.text_pdf_url.find('#')
            if sep != -1:
                extension = '.zip'

            tmp_pdf_path = os.path.join(self.__tmp_dir, task.key() + extension)
            task.download_text_pdf(tmp_pdf_path)

            if sep != -1:
                in_zip_path = task.text_pdf_url[sep+1:]
                with zipfile.ZipFile(tmp_pdf_path) as zfile:
                    matches = []
                    for name in zfile.namelist():
                        if fnmatch.fnmatch(name, in_zip_path):
                            matches.append(name)
                    if len(matches) != 1:
                        print(in_zip_path)
                        raise Exception('Wrong number of matches')
                    zfile.extract(matches[0], self.__tmp_dir)
                os.remove(tmp_pdf_path)
                tmp_pdf_path = os.path.join(self.__tmp_dir, matches[0])

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

    def __save_task_tests(self, task):
        try:
            tmp_zip_path = os.path.join(self.__tmp_dir, task.key() + '.zip')
            task.download_tests_zip(tmp_zip_path)
            _, pat, rep, _ = task.tests_in_to_out.split('/')
            
            with zipfile.ZipFile(tmp_zip_path) as zfile:
                num_matches = 0
                for name in zfile.namelist():
                    if fnmatch.fnmatch(name, os.path.normpath(task.tests_in_path)):
                        filename = os.path.basename(name)
                        dirname = os.path.dirname(name)
                        if not filename:
                            continue
                        _extract_as(zfile, name, os.path.join(
                            self.task_path(task), filename))
                        filename = filename.replace(pat, rep)
                        _extract_as(zfile, os.path.join(dirname, filename), 
                            os.path.join(self.task_path(task), filename))
                        num_matches += 1
                if num_matches != task.tests_num_io:
                    raise Exception('Wrong number of test cases.')
        finally:
            os.remove(tmp_zip_path)
