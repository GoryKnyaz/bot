from zipfile import ZipFile

from openpyxl import load_workbook
from xlwt import Workbook


def write_to_excel(filename, headlines, mass):
    book = Workbook()
    sh = book.add_sheet('АБ-тест результаты')
    for index, headline, value in enumerate(zip(headlines, mass)):
        sh.write(0, index, headline)
        sh.write(1, index, value)
    book.save(filename)


class Reader:

    def __init__(self, path_to_file=''):
        self.data = None
        self.path_to_file = None
        if path_to_file != '':
            self.read(path_to_file)

    def read(self, path_to_file):
        self.path_to_file = path_to_file
        self.data = []
        if path_to_file.endswith('txt'):
            with open(path_to_file, encoding="utf8") as txt_file:
                self.data = [data for data in txt_file.readlines()]
        elif path_to_file.endswith('xlsx'):
            workbook = load_workbook(path_to_file)
            worksheet = workbook.active
            for col in worksheet.iter_cols(1, worksheet.max_column):
                for row in range(0, worksheet.max_row):
                    if col[row].value is not None:
                        self.data.append(col[row].value)
        elif path_to_file.endswith('zip'):
            with ZipFile(path_to_file) as archive:
                for archive_filename in archive.namelist():
                    if archive_filename.endswith('txt'):
                        with archive.open(archive_filename) as txt_file:
                            self.data.append([data.decode() for data in txt_file.readlines()])
