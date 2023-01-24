from time import time

from easygui import fileopenbox
from telebot import *

from config import TOKEN
from db_reader import Reader, write_to_excel
from finder_regex import Finder
from psql import PSQL

markers = ['Реклама курсов', 'Реклама тг-каналов', 'Реклама товаров на маркетплейсах']


class ABTest:

    def __init__(self):
        self.my_chat_id = 0
        self.my_PSQL = PSQL()
        self.my_finder = Finder()
        self.my_dataset = Reader()
        self.is_selects_file = False
        self.is_dataset_selected = False
        self.my_bot = telebot.TeleBot(TOKEN)

    def reset(self):
        self.my_chat_id = 0
        self.my_PSQL = PSQL()
        self.my_finder = Finder()
        self.my_dataset = Reader()
        self.is_selects_file = False
        self.is_dataset_selected = False

    def authorization(self, text):
        user_data = text.split(' ')
        if len(user_data) == 2:
            if self.my_PSQL.authorization(user_data[0], user_data[1]):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for marker in markers:
                    button = types.KeyboardButton(marker)
                    markup.add(button)
                self.my_bot.send_message(self.my_chat_id,
                                         '✅Доступ разрешен.\nВыберете маркер регулярных выражений',
                                         reply_markup=markup)
            else:
                self.my_bot.send_message(self.my_chat_id, '❌В доступе отказано')
        else:
            self.my_bot.send_message(self.my_chat_id, '❌Неправильно введен логин и пароль')

    def set_marker(self, text):
        if text in markers:
            self.my_finder.marker = text
            self.my_bot.send_message(self.my_chat_id, '✅Маркер выбран успешно.',
                                     reply_markup=telebot.types.ReplyKeyboardRemove())
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button = types.KeyboardButton("📝Файл")
            markup.add(button)
            self.my_bot.send_message(self.my_chat_id, 'Нажмите на кнопку и выберете датасет', reply_markup=markup)
        else:
            self.my_bot.send_message(self.my_chat_id, '❌Такого маркера нет. Попробуете еще раз.')

    def select_dataset(self):
        self.is_selects_file = True
        path_to_dataset = fileopenbox(filetypes=['*.txt', '*.zip', '*.xlsx'])
        if path_to_dataset != '':
            try:
                self.my_dataset.read(path_to_dataset)
                self.my_bot.send_message(self.my_chat_id, '✅Файл прочитан успешно.',
                                         reply_markup=telebot.types.ReplyKeyboardRemove())
                self.is_dataset_selected = True
            except ...:
                self.my_bot.send_message(self.my_chat_id, '❌Невозможно распознать датасет. Выберете другой.')
        self.is_selects_file = False

    def ab_test(self):
        result = []
        for regex_mass in self.my_PSQL.parsing_by('marker', self.my_finder.marker)[1:]:
            begin_time = time()
            self.my_finder.reg_ex = regex_mass[2]
            self.my_finder.findInMass(self.my_dataset.data)
            result.append(regex_mass[1:] + [time() - begin_time])
        write_to_excel('Результаты.xlsx', ['Маркер', 'Рег_выражение', 'Версия', 'Время поиска'], result)
        with open('Результаты.xlsx', 'rb') as xlsx_file:
            self.my_bot.send_document(self.my_chat_id, xlsx_file)

    def main(self, text):
        if not self.my_PSQL.is_authorized:
            self.authorization(text)
            self.my_PSQL.create_default_table()
        elif self.my_finder.marker == '':
            self.set_marker(text)
        elif text == '📝Файл' and not self.is_selects_file and not self.is_dataset_selected:
            self.select_dataset()
            self.ab_test()
