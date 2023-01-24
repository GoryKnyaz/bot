from abtest import ABTest, telebot

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
    ab_test.main(message.text)


ab_test.my_bot.polling(none_stop=True, interval=0)
ab_test.my_bot.send_message(ab_test.my_chat_id, "✋Пока-пока✋")
