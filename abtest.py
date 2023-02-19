import os

import telebot

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
        self.my_PSQL = PSQL()
        self.my_finder = Finder()
        self.my_dataset = Reader()
        self.is_dataset_selected = False

    def reset(self):
        """
        A function to reset all data.
        """
        self.my_PSQL = PSQL()
        self.my_finder = Finder()
        self.my_dataset = Reader()
        self.is_dataset_selected = False

    def authorization(self, bot, text, dbname, chat_id):
        """
        A function for user authorization in PostgreSQL via telegram.
        :param dbname: name of server database
        :type dbname: str
        :param bot: object of telegram-bot
        :type bot: TeleBot
        :param text: string of user message.
        :type text: str
        :param chat_id: chat param id
        :type chat_id: int
        """
        user_data = []
        for text_split in text.split(' '):
            if text_split:
                user_data.append(text_split)
        if len(user_data) == 2:
            if self.my_PSQL.authorization(user_data[0], user_data[1], dbname):
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for marker in markers:
                    button = telebot.types.KeyboardButton(marker)
                    markup.add(button)
                bot.send_message(chat_id,
                                 '✅Доступ разрешен.\nВыберете маркер регулярных выражений',
                                 reply_markup=markup)
            else:
                bot.send_message(chat_id, '❌В доступе отказано')
        else:
            bot.send_message(chat_id, '❌Неправильно введен логин и пароль')

    def set_marker(self, bot, text, chat_id):
        """
        A function for set marker of regular expression via telegram.
        :param bot: object of telegram-bot
        :type bot: TeleBot
        :param text: string of user message.
        :type text: str
        :param chat_id: chat param id
        :type chat_id: int
        """
        if text in markers:
            self.my_finder.marker = text
            bot.send_message(chat_id, '✅Маркер выбран успешно.',
                             reply_markup=telebot.types.ReplyKeyboardRemove())
            bot.send_message(chat_id, 'Отправте мне файл с датасетом '
                                      '(я принимаю только \'txt\', \'xlsx\', \'zip\' с \'txt\')')
        else:
            bot.send_message(chat_id, '❌Такого маркера нет. Попробуете еще раз.')

    def select_dataset(self, bot, file_name, file_info, chat_id):
        """
        A function for setting a dataset in a file via telegram.
        :param bot: object of telegram-bot
        :type bot: TeleBot
        :param file_name: name of file
        :type file_name: str
        :param file_info: class stored information about file
        :type file_info: class:`telebot.types.File`
        :param chat_id: chat param id
        :type chat_id: int

        :rtype: bool
        :return: True if the file was successfully downloaded and read, otherwise False
        """
        if file_name.endswith('txt') or file_name.endswith('xlsx') or file_name.endswith('zip'):
            try:
                downloaded_file = bot.download_file(file_info.file_path)
                if not os.path.exists(f'user_files/user_{chat_id}'):
                    os.mkdir(f'user_files/user_{chat_id}')
                with open(f'user_files/user_{chat_id}/{file_name}', 'wb') as new_file:
                    new_file.write(downloaded_file)
                self.my_dataset.read(f'user_files/user_{chat_id}/{file_name}')
                bot.send_message(chat_id, '✅Файл прочитан успешно.',
                                 reply_markup=telebot.types.ReplyKeyboardRemove())
                self.is_dataset_selected = True
            except telebot.apihelper.ApiTelegramException:
                bot.send_message(chat_id, '❌Невозможно распознать датасет. Выберете другой.')
                return False
            except telebot.apihelper.ConnectionError:
                bot.send_message(chat_id, 'Отошел, буду скоро).')
                return False
        else:
            bot.send_message(chat_id,
                             '❌Этот формат я не понимаю, загрузите txt, xlsx или zip с txt внутри.')
            return False
        return True

    def ab_test(self, bot, chat_id):
        """
        A function executed ab-test via telegram.
        :param bot: object of telegram-bot
        :type bot: TeleBot
        :param chat_id: chat param id
        :type chat_id: int
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
            bot.send_document(chat_id, xlsx_file)
        bot.send_message(chat_id, 'Можно присылать и дальше присылать датасеты, чтобы выполнить АБ-тест, но '
                                  'если нужно начать заново, то напиши \'/start\'')

    def download(self, bot, file_name, file_info, chat_id):
        """
        A function downloading the file necessary for ABtest
        :param bot: object of telegram-bot
        :type bot: TeleBot
        :param file_name: name of file
        :type file_name: str
        :param file_info: class stored information about file
        :type file_info: class:`telebot.types.File`
        :param chat_id: chat param id
        :type chat_id: int

        :rtype: bool
        :return: True if the connection is active, False otherwise
        """
        try:
            if self.my_finder.marker:
                if self.select_dataset(bot, file_name, file_info, chat_id):
                    self.ab_test(bot, chat_id)
            else:
                bot.send_message(chat_id, 'Ну и зачем ты мне это прислал?')
        except telebot.apihelper.ConnectionError:
            bot.send_message(chat_id, 'Отошел, буду скоро).')
            return False
        return True

    def text(self, bot, text, dbname, chat_id):
        """
        A function that provides all the necessary logic to execute ab-test.
        :param bot: object of telegram-bot
        :type bot: TeleBot
        :param text: string of user message.
        :type text: str
        :param dbname: name of server database
        :type dbname: str
        :param chat_id: chat param id
        :type chat_id: int

        :rtype: bool
        :return: True if the connection is active, False otherwise
        """
        try:
            if not self.my_PSQL.is_authorized:
                self.authorization(bot, text, dbname, chat_id)
            elif not self.my_finder.marker:
                self.set_marker(bot, text, chat_id)
            else:
                bot.send_message(chat_id, 'Я все еще жду свой файл с датасетом')
        except telebot.apihelper.ConnectionError:
            bot.send_message(chat_id, 'Отошел, буду скоро).')
            return False
        return True
