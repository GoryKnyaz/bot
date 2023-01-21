import csv
import openpyxl
import zipfile


class Reader:

    def __init__(self, filename=''):
        self.filename = filename
        self.data = self.read(filename) if filename != '' else []

    def read(self, filename):
        self.filename = filename
        match filename.split('.')[-1]:
            case 'txt':
                with open(filename) as txt_file:
                    return [data for data in txt_file.read()]
            case 'csv':
                with open(filename) as csv_file:
                    reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
                    return [row for row in reader]
            case 'xlxs':
                workbook = openpyxl.load_workbook(filename)
                worksheet = workbook.active
                return [col[row].value for row in range(0, worksheet.max_row)
                              for col in worksheet.iter_cols(1, worksheet.max_column)]
            case 'zip':
                with zipfile.ZipFile(filename) as archive:
                    for archive_filename in archive.namelist():
                        if archive_filename.split('.') == 'txt':
                            with open(archive_filename) as txt_file:
                                return [data for data in txt_file.read()]
        return []


