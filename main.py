import os
import datetime

import telebot
from telebot import types

from config import token, owner_id
from database import *
from translator import Translate, language_text
from analysis import statistic
from other_translate import document_translate, picture_translate

print("Active")

search_table()
bot = telebot.TeleBot(token)
max_page = 4


def inline_button(page):
    markup = types.InlineKeyboardMarkup()

    # on every page
    previous_page = types.InlineKeyboardButton("<", callback_data='back')
    which_page = types.InlineKeyboardButton(f"{page}/{max_page}", callback_data='pm')
    next_page = types.InlineKeyboardButton(">", callback_data='next')

    if page == 1:
        # page 1
        markup.add(types.InlineKeyboardButton("Русский", callback_data='ru'))
        markup.add(types.InlineKeyboardButton("Английский", callback_data='en'))
        markup.add(types.InlineKeyboardButton("Немецкий", callback_data='de'))
        markup.add(previous_page, which_page, next_page)

    if page == 2:
        # page 2
        markup.add(types.InlineKeyboardButton("Белорусский", callback_data='be'))
        markup.add(types.InlineKeyboardButton("Украинский", callback_data='uk'))
        markup.add(types.InlineKeyboardButton("Казахский", callback_data='kk'))
        markup.add(previous_page, which_page, next_page)

    if page == 3:
        # page 3
        markup.add(types.InlineKeyboardButton("Французский", callback_data='fr'))
        markup.add(types.InlineKeyboardButton("Испанский", callback_data='es'))
        markup.add(types.InlineKeyboardButton("Итальянский", callback_data='it'))
        markup.add(previous_page, which_page, next_page)

    if page == 4:
        # page 4
        markup.add(types.InlineKeyboardButton("Китайский", callback_data='zh-cn'))
        markup.add(types.InlineKeyboardButton("Японский", callback_data='ja'))
        markup.add(types.InlineKeyboardButton("Корейский", callback_data='ko'))
        markup.add(previous_page, which_page, next_page)

    return markup


# First launch and language change
@bot.message_handler(commands=["start", "language"])
def start(message):
    get_value = Database(message.from_user.id)
    if get_value.get_first_start():
        bot.send_message(message.chat.id, 'Выберите на какой язык переводить:', reply_markup=inline_button(get_value.get_page()))
        save_value(message.from_user.id, first_start=False)
    else:
        markup = types.InlineKeyboardMarkup()
        change_language = types.InlineKeyboardButton("Сменить язык", callback_data='menu')
        markup.add(change_language)
        bot.send_message(message.chat.id, f"Вы переводите на {language_text(get_value.get_language())} язык", reply_markup=markup)


# Deleting user data
@bot.message_handler(commands=["delete"])
def delete_id(message):
    get_value = Database(message.from_user.id, delete=True)

    if get_value.get_delete_user():
        markup = types.InlineKeyboardMarkup()
        reestablish = types.InlineKeyboardButton("Восстановить", callback_data='res')
        markup.add(reestablish)
        bot.send_message(message.from_user.id, "Восстановить ваши данные?", reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        delete = types.InlineKeyboardButton("Удалить", callback_data='del')
        markup.add(delete)
        bot.send_message(message.from_user.id, "Удалить ваши данные?", reply_markup=markup)


# Enable / Disable auto text checking
@bot.message_handler(commands=["spelling"])
def switching_spelling(message):
    get_value = Database(message.from_user.id)

    markup = types.InlineKeyboardMarkup()
    spelling_on = types.InlineKeyboardButton("Включить", callback_data='on')
    spelling_of = types.InlineKeyboardButton("Выключить", callback_data='off')

    if get_value.get_spelling():
        markup.add(spelling_of)
        bot.send_message(message.chat.id, 'Автоматическая проверка текста включена',
                         reply_markup=markup)
    else:
        markup.add(spelling_on)
        bot.send_message(message.chat.id, 'Автоматическая проверка текста выключена.\n\nОбратите внимание, '
                                          'при включение данной функции, ответ от бота возможно будет дольше',
                         reply_markup=markup)


# Database analysis
@bot.message_handler(commands=["analysis"])
def analysis(message):
    try:
        if message.chat.id == owner_id:
            bot.send_message(message.chat.id, statistic())
    except AttributeError:
        bot.send_message(message.chat.id, "Ошибка")


# Inline button
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    req = call.data.split('_')
    get_value = Database(call.from_user.id)

    if req[0] in ['next', 'back', 'menu', 'pm']:
        page = get_value.get_page()
        if req[0] == 'next':
            if page < max_page:
                page += 1
            else:
                page = 1
            save_value(call.from_user.id, page=page)

        if req[0] == 'back':
            if page > 1:
                page -= 1
            else:
                page = max_page
            save_value(call.from_user.id, page=page)

        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inline_button(page))

    # Reestablish
    elif req[0] == 'res':
        # Get_Database automatically restores data
        markup = types.InlineKeyboardMarkup()
        delete = types.InlineKeyboardButton("Удалить", callback_data='del')
        markup.add(delete)
        bot.edit_message_text('Данные восстановлены. Удалить ваши данные?',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Delete
    elif req[0] == 'del':
        delete_data(call.from_user.id)
        markup = types.InlineKeyboardMarkup()
        reestablish = types.InlineKeyboardButton("Восстановить", callback_data='res')
        markup.add(reestablish)
        bot.edit_message_text('Данные удалены. Восстановить ваши данные?',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)

    # spelling on
    elif req[0] == 'on':
        save_value(call.from_user.id, spelling=True)
        markup = types.InlineKeyboardMarkup()
        spelling_on = types.InlineKeyboardButton("Выключить", callback_data='off')
        markup.add(spelling_on)
        bot.edit_message_text('Автоматическая проверка текста включена',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # spelling off
    elif req[0] == 'off':
        save_value(call.from_user.id, spelling=False)
        markup = types.InlineKeyboardMarkup()
        spelling_of = types.InlineKeyboardButton("Включить", callback_data='on')
        markup.add(spelling_of)
        bot.edit_message_text('Автоматическая проверка текста выключена\n\nОбратите внимание, '
                              'при включение данной функции, ответ от бота возможно будет дольше',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Choice language
    else:
        save_value(call.from_user.id, language=req[0])
        markup = types.InlineKeyboardMarkup()
        change_language = types.InlineKeyboardButton("Сменить язык", callback_data='menu')
        markup.add(change_language)
        bot.edit_message_text(f'Вы переводите на {language_text(req[0])} язык',
                              reply_markup=markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id)


# Document Translate
@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        bot.send_message(message.chat.id, 'Подождите...')
        # Download file
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # File path
        src = message.document.file_name
        # File translate
        document = document_translate(message.from_user.id, downloaded_file, src)
        if not document:
            bot.edit_message_text("Неподдерживаемый тип файла", message.chat.id, message.id + 1)
        # No errors
        else:
            with open("Перевод.txt", 'r', encoding='utf-8') as file:
                bot.send_document(message.chat.id, file)
            os.remove("Перевод.txt")
        os.remove(src)
        bot.delete_message(message.chat.id, message.id + 1)
    except:
        bot.edit_message_text("Неподдерживаемый тип файла", message.chat.id, message.id + 1)


# Picture translate
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.send_message(message.chat.id, "Подождите...")
        # Download file
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # File translate
        picture = picture_translate(message.from_user.id, downloaded_file)
        bot.edit_message_text(f"Распознанный текст:\n\n{picture['text_recognition']}\n\nПеревод:\n\n{picture['result']}", message.chat.id, message.id + 1)
        try:
            os.remove("translate.jpg")
        except FileNotFoundError:
            pass
    except:
        bot.edit_message_text("Произошла неизвестная ошибка. Повторите попытку", message.chat.id, message.id + 1)


# Message from user for translation
@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, 'Подождите...')
    get_value = Database(message.from_user.id)
    translate = Translate()
    # translation with spell check
    if get_value.get_spelling():
        message_translation = translate.auto_spelling(message.text.strip(), get_value.get_language())
        if message_translation['errors_found']:
            bot.edit_message_text(message_translation['spelling_text'], message.chat.id, message.id + 1, parse_mode="Markdown")
        bot.send_message(message.chat.id, message_translation['result'])
    else:
        bot.edit_message_text(translate.translate(message.text.strip(), get_value.get_language()), message.chat.id, message.id + 1)


bot.polling(none_stop=True, interval=0, timeout=25)