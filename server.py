from datetime import datetime

from abtest import ABTest, PSQL, telebot
from config import TOKEN


class Server:
    """
    Server class for storing data about all active users, for receiving and adding data about users
    """

    def __init__(self):
        """
        Constructor.
        """
        self.my_bot = telebot.TeleBot(TOKEN)
        self.my_datas = {}
        self.dbname = 'TGServer'
        PSQL().create_default_database()

    def __del__(self):
        """
        Destructor.
        """
        self.my_bot.close()
        self.my_datas.clear()

    def get_current(self, index):
        """
        Getting information about a specific user
        :param index:
        :type: int

        :rtype: Any
        :return: information about a specific user
        """
        self.clear_old_connect()
        try:
            current = self.my_datas[index]
            current[0] = datetime.now()
        except KeyError:
            return None
        return current[1]

    def set_current(self, index, data):
        """
        Adding a user
        :param index:
        :type: int
        :param data:
        :type: Any

        :rtype: bool
        :return: True if array is not full, otherwise False
        """
        if len(self.my_datas) <= 1000:
            self.my_datas[index] = [datetime.now(), data]
            print(f"Number: {len(self.my_datas)}, id: {index}")
            return True
        return False

    def clear_old_connect(self):
        """
        Removing all users who have not sent requests for a long time
        """
        deleted_users = 0
        for data in list(self.my_datas):
            date = datetime.now() - self.my_datas[data][0]
            if date.seconds >= 3600:
                deleted_users += 1
                del self.my_datas[data]
        if deleted_users:
            print(f"Deleted users: {deleted_users} :-(")

    def turn_on(self):
        """
        Enable the bot
        """
        self.my_bot.polling(none_stop=True, interval=0)


my_server = Server()


@my_server.my_bot.message_handler(commands=['start'])
def start(message):
    """
        A function that handles the launch command when the bot is resolved.
        :param message: class object containing all information about the telegram bot.
        :type: Message
    """
    is_not_full = True
    chat_id = message.chat.id
    ab_test = my_server.get_current(chat_id)
    if ab_test is None:
        is_not_full = my_server.set_current(chat_id, ABTest())
    else:
        ab_test.reset()
    my_server.my_bot.send_message(chat_id,
                                  '✋Привет, я бот, созданный для AB-теста регулярных выражений. '
                                  'Вводите в PostgreSQL, если он у вас есть. Введите логин и пароль через пробел:'
                                  if is_not_full else
                                  '💀Извините, но сервер уже перегружен!',
                                  reply_markup=telebot.types.ReplyKeyboardRemove())


@my_server.my_bot.message_handler(content_types=['text'])
def text(message):
    """
        A function that processes the user's regular messages.
        :param message: class object containing all information about the telegram bot.
        :type: Message
    """
    chat_id = message.chat.id
    ab_test = my_server.get_current(chat_id)
    if ab_test is not None:
        ab_test.text(my_server.my_bot, message.text, my_server.dbname, chat_id)
    else:
        is_not_full = my_server.set_current(chat_id, ABTest())
        my_server.my_bot.send_message(chat_id,
                                      '⚠Ой, кажется все данные о вас были потерены. Но мы вас заново загрузили. '
                                      'Пожалуйста, заново вводите в PostgreSQL, если он у вас есть. '
                                      'И заново введите логин и пароль через пробел:'
                                      if is_not_full else
                                      '💀Извините, но сервер уже перегружен!',
                                      reply_markup=telebot.types.ReplyKeyboardRemove())


@my_server.my_bot.message_handler(content_types=['document'])
def download_document(message):
    """
        A function that processes the user's regular messages.
        :param message: class object containing all information about the telegram bot.
        :type: Message
    """
    chat_id = message.chat.id
    ab_test = my_server.get_current(chat_id)
    if ab_test is not None:
        ab_test.download(my_server.my_bot, message.document.file_name,
                         my_server.my_bot.get_file(message.document.file_id), chat_id)
    else:
        is_not_full = my_server.set_current(chat_id, ABTest())
        my_server.my_bot.send_message(chat_id,
                                      '⚠Ой, кажется все данные о вас были потерены. Но мы вас заново загрузили. '
                                      'Пожалуйста, заново вводите в PostgreSQL, если он у вас есть. '
                                      'И заново введите логин и пароль через пробел:'
                                      if is_not_full else
                                      '💀Извините, но сервер уже перегружен!',
                                      reply_markup=telebot.types.ReplyKeyboardRemove())
