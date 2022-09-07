from googletrans import Translator
import telebot
from telebot import types
import config as r
import datetime, os
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
print("Active")
class Language:
    lang = "en"
l = Language()
bot = telebot.TeleBot(r.token)
list_lang = ["ru", "Русский", "en", "Английский", "Украинский", "uk", "Армянский", "hy"]
@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup=types.InlineKeyboardMarkup()
    item1=types.InlineKeyboardButton("Русский",  callback_data='pwd1')
    item2=types.InlineKeyboardButton("Английский",  callback_data='pwd2')
    item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    bot.send_message(message.chat.id, f'Выберите на какой язык переводить:',  reply_markup=markup)
@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    req = call.data.split('_')
    if req[0] == 'pwd1':
        l.lang = "ru"
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Русский язык', reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd2':
        l.lang = "en"
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Английский язык', reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd3':
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
        item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
        item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
        markup.add(item1)
        markup.add(item2)
        markup.add(item3)
        bot.edit_message_text(f'Выберите на какой язык переводить:', reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd4':
        l.lang = "de"
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Немецкий язык', reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = message.document.file_name

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        with open(src, 'r+', encoding= 'utf-8') as file:
            text = file.read()
            if len(text) > 10000:
                bot.send_message(message.chat.id, "Файл слишком большой, придется подождать")
            translator = Translator()
            result = translator.translate(text, dest=l.lang)
        with open("Перевод.txt", 'w+', encoding= 'utf-8') as file:
            file.write(result.text)
        with open("Перевод.txt", 'r', encoding= 'utf-8') as file:
            bot.send_document(message.chat.id, file)
        try:
            os.remove(src)
            os.remove("Перевод.txt")
        except:
            pass
    except:
        bot.send_message(message.chat.id, "Произошка ошибка, пожалуйста отправьте документ еще раз")
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[0].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = message.photo[0].file_id
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        with Image.open(src) as file:
            string = pytesseract.image_to_string(file)
            translator = Translator()
            result = translator.translate(string, dest=l.lang)
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
            markup.add(item1)
            if result.text == "":
                bot.send_message(message.chat.id, f"На изображении ничего не расспознанно.", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f"Распознанный текст: {string}\n\nПеревод: [{l.lang}] {result.text}", reply_markup=markup)
        try:
            os.remove(src)
        except:
            print("Error")
    except:
        bot.send_message(message.chat.id, "Произошка ошибка, пожалуйста отправьте фото еще раз")
@bot.message_handler(content_types=["text"])
def handle_text(message):
    try:
        translator = Translator()
        result = translator.translate(message.text, dest=l.lang)
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.send_message(message.chat.id, f'[{l.lang}] {result.text}',  reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "Произошка ошибка, пожалуйста введите сообщение еще раз")
bot.polling(none_stop=True, interval=0)