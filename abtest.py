from telebot import *
from easygui import fileopenbox

from psql import PSQL
from config import TOKEN
from db_reader import Reader
from finder_regex import Finder


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

    def authorization(self, message):
        user_data = message.text.split(' ')
        if len(user_data) == 2:
            if self.my_PSQL.authorization(user_data[0], user_data[1]):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button = types.KeyboardButton("📝Файл")
                markup.add(button)
                self.my_bot.send_message(self.my_chat_id,
                                         '✅Доступ разрешен.\nНажмите на кнопку и выберете датасет',
                                         reply_markup=markup)
            else:
                self.my_bot.send_message(self.my_chat_id, '❌В доступе отказано')
        else:
            self.my_bot.send_message(self.my_chat_id, '❌Неправильно введен логин и пароль')

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
