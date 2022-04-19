import googletrans
from googletrans import Translator
import telebot
from telebot import types
class Language:
    lang = "en"
l = Language()
bot = telebot.TeleBot("5346709603:AAFoBDCnJOSE98LXRGuxNX72WgBe368SWqI")    
@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Русский")
    item2=types.KeyboardButton("English")
    item3=types.KeyboardButton("Український")
    markup.add(item1)
    markup.add(item3)
    markup.add(item2)
    
    bot.send_message(message.chat.id, f'Выберите на какой язык переводить:',  reply_markup=markup)
@bot.message_handler(content_types=["ru"])
def ru_leng(message):
    l.lang = "ru"
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    bot.send_message(message.chat.id, f'Ваш язык: Русский\nНапишите слово или предложение которое нужно перевести\n\nДля смены языка напишите /start',  reply_markup=markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == "ru" or message.text.strip() == "Русский":
        l.lang = "ru"
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("/start")
        markup.add(item1)
        bot.send_message(message.chat.id, f'Вы переводите на Русский язык \nНапишите слово или предложение которое нужно перевести\n\nДля смены языка напишите /start',  reply_markup=markup)
    if message.text.strip() == "en" or message.text.strip() == "English":
        l.lang = "en"
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("/start")
        markup.add(item1)
        bot.send_message(message.chat.id, f'Вы переводите на Английский язык \nНапишите слово или предложение которое нужно перевести\n\nДля смены языка напишите /start',  reply_markup=markup)
    if message.text.strip() == "uk" or message.text.strip() == "Український":
        l.lang = "uk"
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("/start")
        markup.add(item1)
        bot.send_message(message.chat.id, f'Вы переводите на Украинский язык \nНапишите слово или предложение которое нужно перевести\n\nДля смены языка напишите /start',  reply_markup=markup)
    if message.text.strip() != "ru" and message.text.strip() != "en" and message.text.strip() != "English" and message.text.strip() != "Русский" and message.text.strip() != "uk" and message.text.strip() != "Український":    
        translator = Translator()
        result = translator.translate(message.text, dest=l.lang)
        print(f"[{message.from_user.first_name}]", message.text)
        print(f"[BOT]", result.text)
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item0=types.KeyboardButton("/start")
        markup.add(item0)
        bot.send_message(message.chat.id, f'[{l.lang}] {result.text}',  reply_markup=markup)
bot.polling(none_stop=True, interval=0)                                         