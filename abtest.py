import telebot
from easygui import fileopenbox

from config import TOKEN
from db_reader import Reader, write_to_excel
from finder_regex import Finder
from psql import PSQL

# The array of available regex markers.
markers = ['Реклама курсов', 'Реклама тг-каналов', 'Реклама товаров на маркетплейсах']


class ABTest:
    """
    The class needed to store all the necessary data to perform the ab-test and to execute it.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.my_chat_id = 0
        self.my_PSQL = PSQL()
        self.my_finder = Finder()
        self.my_dataset = Reader()
        self.is_selects_file = False
        self.is_dataset_selected = False
        self.my_bot = telebot.TeleBot(TOKEN)

    def reset(self):
        """
        A function to reset all data.
        """
        self.my_chat_id = 0
        self.my_PSQL = PSQL()
        self.my_finder = Finder()
        self.my_dataset = Reader()
        self.is_selects_file = False
        self.is_dataset_selected = False

    def authorization(self, text):
        """
        A function for user authorization in PostgreSQL via telegram.
        :param str text: string of user message.
        """
        user_data = []
        for text_spliting in text.split(' '):
            if text_spliting:
                user_data.append(text_spliting)
        if len(user_data) == 2:
            if self.my_PSQL.authorization(user_data[0], user_data[1]):
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for marker in markers:
                    button = telebot.types.KeyboardButton(marker)
                    markup.add(button)
                self.my_bot.send_message(self.my_chat_id,
                                         '✅Доступ разрешен.\nВыберете маркер регулярных выражений',
                                         reply_markup=markup)
            else:
                self.my_bot.send_message(self.my_chat_id, '❌В доступе отказано')
        else:
            self.my_bot.send_message(self.my_chat_id, '❌Неправильно введен логин и пароль')

    def set_marker(self, text):
        """
        A function for set marker of regular expression via telegram.
        :param text: string of user message.
        """
        if text in markers:
            self.my_finder.marker = text
            self.my_bot.send_message(self.my_chat_id, '✅Маркер выбран успешно.',
                                     reply_markup=telebot.types.ReplyKeyboardRemove())
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            button = telebot.types.KeyboardButton("📝Файл")
            markup.add(button)
            self.my_bot.send_message(self.my_chat_id, 'Нажмите на кнопку и выберете датасет', reply_markup=markup)
        else:
            self.my_bot.send_message(self.my_chat_id, '❌Такого маркера нет. Попробуете еще раз.')

    def select_dataset(self):
        """
        A function for setting a dataset in a file via telegram.
        """
        self.is_selects_file = True
        path_to_dataset = fileopenbox(filetypes=['*.txt', '*.zip', '*.xlsx'])
        if path_to_dataset != '':
            try:
                self.my_bot.send_message(self.my_chat_id,
                                         'Открылось окно, если оно не появилось, то сверните все вкладки')
                self.my_dataset.read(path_to_dataset)
                self.my_bot.send_message(self.my_chat_id, '✅Файл прочитан успешно.',
                                         reply_markup=telebot.types.ReplyKeyboardRemove())
                self.is_dataset_selected = True
            except telebot.ExceptionHandler:
                self.my_bot.send_message(self.my_chat_id, '❌Невозможно распознать датасет. Выберете другой.')
        self.is_selects_file = False

    def ab_test(self):
        """
        A function executed ab-test via telegram.
        :return:
        """
        result = []
        for regex_mass in self.my_PSQL.parsing_by('marker', self.my_finder.marker)[1:]:
            begin_time = telebot.time.time_ns()
            self.my_finder.reg_ex = fr'{regex_mass[2]}'
            finding_mass = self.my_finder.findInMass(self.my_dataset.data)
            finding_count = 0
            for finding_elements in finding_mass:
                finding_count += (len(finding_elements) if len(finding_elements) > 0 else 0)
            result.append(regex_mass[1:] + [(telebot.time.time_ns() - begin_time) / 1000, finding_count])
        write_to_excel('Результаты.xls',
                       ['Маркер', 'Рег_выражение', 'Версия', 'Время поиска(милисек.))', 'Кол-во совпадений'], result)
        with open('Результаты.xls', 'rb') as xlsx_file:
            self.my_bot.send_document(self.my_chat_id, xlsx_file)
        self.my_bot.send_message(self.my_chat_id, 'Для выполения АБ-теста напиши \'/start\'')

    def main(self, text):
        """
        A function that provides all the necessary logic to execute ab-test.
        :param text: string of user message.
        """
        if not self.my_PSQL.is_authorized:
            self.authorization(text)
        elif not self.my_PSQL.conn:
            self.my_PSQL.create_default_table()
        elif not self.my_finder.marker:
            self.set_marker(text)
        elif text == '📝Файл' and not self.is_selects_file and not self.is_dataset_selected:
            self.select_dataset()
            self.ab_test()
