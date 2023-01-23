import openpyxl
import zipfile


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
            workbook = openpyxl.load_workbook(path_to_file)
            worksheet = workbook.active
            for col in worksheet.iter_cols(1, worksheet.max_column):
                for row in range(0, worksheet.max_row):
                    if col[row].value is not None:
                        self.data.append(col[row].value)
        elif path_to_file.endswith('zip'):
            with zipfile.ZipFile(path_to_file) as archive:
                for archive_filename in archive.namelist():
                    if archive_filename.endswith('txt'):
                        with archive.open(archive_filename) as txt_file:
                            self.data.append([data.decode() for data in txt_file.readlines()])
