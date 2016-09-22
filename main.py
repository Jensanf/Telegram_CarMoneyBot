# -*- coding: utf-8 -*-

# todo Добавить возможность выбора автомобиля
# todo Добавить обработку разных видов расходов
# todo Добавить выбор валюты
# todo Отмена действия
# todo Общие автомобили
# todo Ввод задним числом

import config
import sqlite3
import telebot
import datetime
from telebot import types

# Uncomment line and paste your token for bot from @BotFather
API_TOKEN = config.token
bot = telebot.TeleBot(API_TOKEN)

bill_dict = {}

class Bill:
    def __init__(self, uid):
        self.number = None
        self.uid = uid
        self.name = None
        self.date = None
        self.car = None
        self.kind = None
        self.distance = None
        self.costs = None
        self.volume = None
        self.price = None
        self.mark = None
        self.comment = None
try:
    con = sqlite3.connect('drivers.db')
    cur = con.cursor()
except:
    # users changed to drivers
    cur.execute('CREATE TABLE drivers (ID INTEGER PRIMARY KEY, '
                'userID real, '
                'name text, '
                'date real,'
                'car text'
                'kindBill text, '
                'distance real, '
                'cost real, '
                'volume real, '
                'price real, '
                'station text'
                'mark real'
                'comments text)')
    con.commit()

# Funcion to control and convert string numbers to float
def isfloat(value):
        try:
            float(value)
            return value
        except ValueError:
            return float(value.replace(',', '.'))

@bot.message_handler(commands=['помощь','help','п'])
def send_welcome(message):
    bot.send_message(message.chat.id,
        'Привет, я твой помошник по расходам автомобиля!'
        + '\n Введите команду согласно виду расхода:'
        + '\n Топливо - /бензин или /fuel или /б'
        + '\n Ремонт - /ремонт или /repair или /р'
        + '\n Мойка - /мойка или /wash или /м'
                     )

@bot.message_handler(commands=['старт','start','с'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Мойка', 'Ремонт', 'Расходники', 'Топливо')
    msg = bot.send_message(message.chat.id,
        'Привет, я твой личный финансовый помошник по расходам автомобиля!'
        + '\nВыберите вид расхода.', reply_markup=markup)
    bot.register_next_step_handler(msg, process_START_step)
def process_START_step(message):
    if (message.text == 'Мойка'):
        user_id = message.chat.id
        bot.send_message(user_id,
                         'Запись трат на "Мойку" находится в разработке! Плюньте в разработчика, и он поморщится! vk.com/jensanf')
    if (message.text == 'Ремонт'):
        user_id = message.chat.id
        bot.send_message(user_id,
                         'Запись трат на "Ремонт" находится в разработке! Плюньте в разработчика, и он поморщится! vk.com/jensanf')
    if (message.text == 'Расходники'):
        user_id = message.chat.id
        bot.send_message(user_id,
                         'Запись трат на "Расходники" находится в разработке! Плюньте в разработчика, и он поморщится! vk.com/jensanf')
    if (message.text == 'Топливо'):
        user_id = message.chat.id
        bot.send_message(user_id,
                         'Запись трат на "Топливо" находится в разработке! Плюньте в разработчика, и он поморщится! vk.com/jensanf')

@bot.message_handler(commands=['бензин', 'fuel','бенз','б'])
def send_welcome(message):
    user_id = message.chat.id
    bill = Bill(user_id)
    bill_dict[user_id] = bill
    bill.date = (datetime.datetime.fromtimestamp(message.date))
    bill.name = message.chat.first_name
    bill.kind = 'Топливо'

    msg = bot.send_message(message.chat.id,
        'Для учёта топлива ответьте на 5 вопросов: '
        + '\n 1. Текущий пробег автомобиля?')
    bot.register_next_step_handler(msg, process_distance_step)
def process_distance_step(message):
    try:
        user_id = message.chat.id
        distance = message.text
        if not distance.replace(',', '').isdigit():
            msg = bot.send_message(user_id, 'Это должно быть число. Какой у вашего автомобиля пробег?')
            bot.register_next_step_handler(msg, process_distance_step)
            return
        bill = bill_dict[user_id]
        bill.distance = isfloat(distance)
        print(bill.distance)
        msg = bot.send_message(user_id, '2. Сколько литров Вы заправили?')
        bot.register_next_step_handler(msg, process_volume_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')
def process_volume_step(message):
    try:
        user_id = message.chat.id
        volume = message.text
        if not volume.replace(',', '').isdigit():
            msg = bot.send_message(message.chat.id, 'Это должно быть число. На сколько литров Вы заправились?')
            bot.register_next_step_handler(msg, process_volume_step)
            return
        bill = bill_dict[user_id]
        bill.volume = isfloat(volume)
        print(bill.volume)
        msg = bot.send_message(message.chat.id, '3. На какую сумму Вы заправились?')
        bot.register_next_step_handler(msg, process_costs_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')
def process_costs_step(message):
    try:
        con = sqlite3.connect('drivers.db')
        cur = con.cursor()
        user_id = message.chat.id
        costs = message.text
        if not costs.replace(',', '').isdigit():
            msg = bot.send_message(message.chat.id, 'Это должно быть число. Какую сумму Вы потратили?')
            bot.register_next_step_handler(msg, process_costs_step)
            return
        bill = bill_dict[user_id]
        bill.costs = isfloat(costs)
        bill.price = round(float(bill.costs)/float(bill.volume), 2)
        print(bill.costs)
        print(format(float(bill.costs)/float(bill.volume), '.2f'))

        cur.execute('SELECT ID FROM users WHERE chatID=(?)', (user_id,))
        bill.number = len(cur.fetchall()) + 1

        bot.send_message(user_id, 'Спасибо за ответы, '+bill.name+'! \nЭто Ваш '
                         + str(message.chat.first_name) + ' счет'
                         + '\n Дата: ' + str(datetime.datetime.fromtimestamp(message.date))
                         + '\n Пробег: ' + str(bill.distance) + ' км.'
                         + '\n Заправлено: ' + str(bill.volume) + ' л. по '
                         + str(bill.price) + ' руб./л'
                         + '\n Сумма чека: ' + str(bill.costs) + ' руб.')
        params = (bill.uid, bill.name, bill.kind, bill.distance, bill.costs, bill.price, bill.volume)
        cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, NULL)", params)
        con.commit()
        cur.execute('SELECT * FROM users')
        print(cur.fetchall())
        con.close()
    except Exception as e:
        bot.reply_to(message, 'oooops')

@bot.message_handler(commands=['ремонт', 'repair', 'rep','р'])
def send_welcome(message):
    user_id = message.chat.id
    bot.send_message(user_id,
        'Функция "Ремонт" находится в разработке! Пните разработчика, и он зашвелится! vk.com/jensanf')

@bot.message_handler(commands=['расходники', 'spares','х'])
def send_welcome(message):
    user_id = message.chat.id
    bot.send_message(user_id,
        'Запись трат на "Расходники" находится в разработке! Напишите разработчику, и он ответит! vk.com/jensanf')

@bot.message_handler(commands=['мойка', 'wash','м'])
def send_welcome(message):
    user_id = message.chat.id
    bot.send_message(user_id,
        'Запись трат на "Мойку" находится в разработке! Плюньте в разработчика, и он поморщится! vk.com/jensanf')

@bot.message_handler(func=lambda message: message.text == "Как дела?" or message.text == "как дела?" or message.text == "Как успехи?")
def command_text_hi(message):
    try:
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        user_id = message.chat.id
        bill = bill_dict[user_id]
        cur.execute('SELECT ID FROM users WHERE chatID=(?)', (user_id,))
        bill.number = len(cur.fetchall()) + 1
        bot.send_message(user_id, 'Всё супер, ' + bill.name + '! \nЭто Ваш '
                         + str(bill.number) + ' счет'
                         + '\n Дата: ' + str(datetime.datetime.fromtimestamp(message.date))
                         + '\n Пробег: ' + str(bill.distance) + ' км.'
                         + '\n Заправлено: ' + str(bill.volume) + ' л. по '
                         + str(bill.price) + ' руб./л'
                         + '\n Сумма чека: ' + str(bill.costs) + ' руб.')
        params = (bill.uid, bill.name, bill.kind, bill.distance, bill.costs, bill.price, bill.volume)
        cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, NULL)", params)
        con.commit()
        con.close()
    except:
        bot.send_message(user_id, 'Пока не известно!')

# filter on a specific message
@bot.message_handler(func=lambda message: message.text == "Привет" or message.text == "привет")
def command_text_hi(m):
    bot.send_message(m.chat.id, "И я тебя люблю!")

bot.polling()