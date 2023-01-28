from abtest import ABTest, telebot

ab_test = ABTest()


@ab_test.my_bot.message_handler(commands=['start'])
def start(message):
    """
        A function that handles the launch command when the bot is resolved.
        :param message: class object containing all information about the telegram bot.
    """
    ab_test.reset()
    ab_test.my_chat_id = message.chat.id
    ab_test.my_bot.send_message(ab_test.my_chat_id,
                                '✋Привет, я бот, созданный для AB-теста регулярных выражений. '
                                'Вводите в PostgreSQL, если он у вас есть. Введите логин и пароль через пробел',
                                reply_markup=telebot.types.ReplyKeyboardRemove())


@ab_test.my_bot.message_handler(content_types=['text'])
def text(message):
    """
        A function that processes the user's regular messages.
        :param message: class object containing all information about the telegram bot.
    """
    ab_test.text(message.text, message.chat.id)


@ab_test.my_bot.message_handler(content_types=['document'])
def download_document(message):
    """
        A function that processes the user's regular messages.
        :param message: class object containing all information about the telegram bot.
    """
    ab_test.download(message)


ab_test.my_bot.polling(none_stop=True, interval=0)
