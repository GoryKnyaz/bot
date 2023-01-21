from telebot import *

from config import TOKEN
from psql import MyPSQL

my_PSQL = MyPSQL()
bot = telebot.TeleBot(TOKEN)


class MyBot(TeleBot):
    def __init__(self):
        pass

    def __del__(self):
        pass


@bot.message_handler(commands=['start'])
def start(message):
    """markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Факт")
    item2 = types.KeyboardButton("Поговорка")
    markup.add(item1)
    markup.add(item2)"""
    bot.send_message(message.chat.id, 'Введите логин и пароль через пробел')


def authorization(message):
    user_data = message.text.split(' ')
    if len(user_data) == 2:
        if my_PSQL.authorization(user_data[0], user_data[1]):
            bot.send_message(message.chat.id, 'Доступ разрешен')
        else:
            bot.send_message(message.chat.id, 'В доступе отказано')
    else:
        bot.send_message(message.chat.id, 'Неправильно введен логин и пароль')


@bot.message_handler(content_types=['text'])
def main(message):
    if not my_PSQL.is_authorized:
        authorization(message)
    else:
        pass


bot.polling(none_stop=True, interval=0)
