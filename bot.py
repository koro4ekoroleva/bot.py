import telebot
import pickle
import sklearn
import pandas
import datetime

# @heart_pred_bot


with (open("heard-model", "rb")) as openfile:
    model = pickle.load(openfile)
    bot = telebot.TeleBot('6339016515:AAFG2mpcR3ArN6nHz1FE_CCurTCRwdln6D0')

age, weight, ap_hi, ap_lo, cholesterol, gluc = [0, 0, 0, 0, 0, 0]


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = telebot.types.InlineKeyboardMarkup()
    buttonA = telebot.types.InlineKeyboardButton('Да', callback_data='a')
    buttonB = telebot.types.InlineKeyboardButton('Нет', callback_data='b')
    buttonC = telebot.types.InlineKeyboardButton('Не знаю', callback_data='c')
    markup.row(buttonA, buttonB)
    markup.row(buttonC)
    bot.send_message(message.chat.id, 'Хотите определить риск сердечно-сосудистых заболеваний?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    if call.data == "a":
        bot.send_message(call.message.chat.id, 'Введите дату рождения в формате "дд.мм.гггг"')
        bot.register_next_step_handler(call.message, get_age)


def get_age(message):
    global age
    x = str(message.text).split('.')
    age = str(x[2]) + '-' + str(x[1]) + '-' + str(x[0]) + ' 00:00:00.0'
    age = datetime.datetime.strptime(age, "%Y-%m-%d  %H:%M:%S.%f").date()
    now = datetime.date.today()
    age = int(str(now - age).split(' ')[0])
    bot.send_message(message.chat.id, 'Введите вес в килограммах')
    bot.register_next_step_handler(message, get_weight)


def get_weight(message):
    global weight
    weight = float(message.text)
    bot.send_message(message.chat.id, 'Введите систолическое АД')
    bot.register_next_step_handler(message, get_ap_hi)


def get_ap_hi(message):
    global ap_hi
    ap_hi = float(message.text)
    bot.send_message(message.chat.id, 'Введите диастолическое АД')
    bot.register_next_step_handler(message, get_ap_lo)


def get_ap_lo(message):
    global ap_lo
    ap_lo = float(message.text)
    markup = telebot.types.InlineKeyboardMarkup()
    cholesterolA = telebot.types.InlineKeyboardButton('В норме', callback_data=1)
    cholesterolB = telebot.types.InlineKeyboardButton('Выше нормы', callback_data=2)
    cholesterolC = telebot.types.InlineKeyboardButton('Значительно выше нормы', callback_data=3)
    markup.row(cholesterolA)
    markup.row(cholesterolB, cholesterolC)
    bot.send_message(message.chat.id, 'Выберите уровень холестерина', reply_markup=markup)



@bot.callback_query_handler()
def get_cholesterol(call):
    global cholesterol
    cholesterol = float(call.data)
    markup = telebot.types.InlineKeyboardMarkup()
    glucA = telebot.types.InlineKeyboardButton('В норме', callback_data=1)
    glucB = telebot.types.InlineKeyboardButton('Выше нормы', callback_data=2)
    glucC = telebot.types.InlineKeyboardButton('Значительно выше нормы', callback_data=3)
    markup.row(glucA)
    markup.row(glucB, glucC)
    bot.send_message(call.message.chat.id, 'Выберите уровень глюкозы')


@bot.callback_query_handler(func=lambda call: True)
def get_gluc(call):
    global gluc
    gluc = float(call.data)
    bot.send_message(call.message.chat.id, 'Нажмите любую клавишу')
    bot.register_next_step_handler(call.message, get_predict)


def get_predict(message):
    global age, weight, ap_hi, ap_lo, cholesterol, gluc
    pred = model.predict([[age, weight, ap_hi, ap_lo, cholesterol, gluc]])
    if pred[0]:
        bot.send_message(message.chat.id, 'Риск сердечно-сосудистых заболеваний велик. Если вы ещё не стоите на учёте '
                                          'у кардиолога, то советуем посетить его!')
    else:
        bot.send_message(message.chat.id, 'Риск сердечно-сосудистых заболеваний мал')
    print(str(pred[0]))
    print(*pred)
bot.polling()