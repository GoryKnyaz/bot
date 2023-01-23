from telebot import *
from abtest import ABTest

ab_test = ABTest()

@ab_test.my_bot.message_handler(commands=['start'])
def start(message):
    ab_test.reset()
    ab_test.my_chat_id = message.chat.id
    ab_test.my_bot.send_message(ab_test.my_chat_id,
                                '✋Привет, я бот, созданный для AB-теста регулярных выражений. '
                                'Вводите в PostgreSQL, если он у вас есть. Введите логин и пароль через пробел',
                                reply_markup=telebot.types.ReplyKeyboardRemove())

@ab_test.my_bot.message_handler(content_types=['text'])
def main(message):
    if not ab_test.my_PSQL.is_authorized:
        ab_test.authorization(message)
    elif message.text == '📝Файл' and not ab_test.is_selects_file and not ab_test.is_dataset_selected:
        ab_test.select_dataset()
    elif ab_test.is_dataset_selected:
        pass


ab_test.my_bot.polling(none_stop=True, interval=0)
ab_test.my_bot.send_message(ab_test.my_chat_id, "✋Пока-пока✋")
