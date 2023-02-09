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
max_page = 5


def inline_button(page):
    markup = types.InlineKeyboardMarkup()

    # on every page
    previous_page = types.InlineKeyboardButton("<", callback_data='back')
    which_page = types.InlineKeyboardButton(f"{page}/{max_page}", callback_data='pm')
    next_page = types.InlineKeyboardButton(">", callback_data='next')

    if page == 1:
        # page 1
        language1 = types.InlineKeyboardButton("Русский", callback_data='ru')
        language2 = types.InlineKeyboardButton("Английский", callback_data='en')
        language3 = types.InlineKeyboardButton("Немецкий", callback_data='de')
        markup.add(language1)
        markup.add(language2)
        markup.add(language3)
        markup.add(previous_page, which_page, next_page)
    if page == 2:
        # page 2
        language4 = types.InlineKeyboardButton("Белорусский", callback_data='be')
        language5 = types.InlineKeyboardButton("Украинский", callback_data='uk')
        language6 = types.InlineKeyboardButton("Армянский", callback_data='hy')

        markup.add(language4)
        markup.add(language5)
        markup.add(language6)
        markup.add(previous_page, which_page, next_page)
    if page == 3:
        # page 3
        language7 = types.InlineKeyboardButton("Французский", callback_data='fr')
        language8 = types.InlineKeyboardButton("Испанский", callback_data='es')
        language9 = types.InlineKeyboardButton("Итальянский", callback_data='it')

        markup.add(language7)
        markup.add(language8)
        markup.add(language9)
        markup.add(previous_page, which_page, next_page)
    if page == 4:
        # page 4
        language10 = types.InlineKeyboardButton("Китайский", callback_data='zh-cn')
        language11 = types.InlineKeyboardButton("Японский", callback_data='ja')
        language12 = types.InlineKeyboardButton("Корейский", callback_data='ko')
        markup.add(language10)
        markup.add(language11)
        markup.add(language12)
        markup.add(previous_page, which_page, next_page)
    if page == 5:
        # page 5
        language13 = types.InlineKeyboardButton("Болгарский", callback_data='bg')
        language14 = types.InlineKeyboardButton("Сербский", callback_data='sr')
        language15 = types.InlineKeyboardButton("Словацкий", callback_data='sk')
        markup.add(language13)
        markup.add(language14)
        markup.add(language15)
        markup.add(previous_page, which_page, next_page)

    return markup


def logs(user, text, type_info='info'):
    time = datetime.datetime.now().strftime("%H:%M:%S")
    with open('logs.txt', 'a+', encoding='utf-8') as file:
        if type_info == 'error':
            file.write(f'[ERROR][{time}][{user}] {text}\n')
        else:
            file.write(f'[INFO][{time}][{user}] {text}\n')


# First launch and language change
@bot.message_handler(commands=["start", "language"])
def start(message):
    get_value = Database(message.from_user.id)
    if get_value.get_first_start():
        logs(message.from_user.id, 'Новый пользователь')
        bot.send_message(message.chat.id, 'Выберите на какой язык переводить:', reply_markup=inline_button(get_value.get_page()))
        save_value(message.from_user.id, first_start=False)
    else:
        logs(message.from_user.id, 'Меняет язык')
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
            logs(call.from_user.id, 'Перешел на следующую страницу')

        if req[0] == 'back':
            if page > 1:
                page -= 1
            else:
                page = max_page
            save_value(call.from_user.id, page=page)
            logs(call.from_user.id, 'Перешел на прошлую страницу')

        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inline_button(page))

    # Reestablish
    elif req[0] == 'res':
        logs(call.from_user.id, 'Восстановил данные')
        # Get_Database automatically restores data
        markup = types.InlineKeyboardMarkup()
        delete = types.InlineKeyboardButton("Удалить", callback_data='del')
        markup.add(delete)
        bot.edit_message_text('Данные восстановлены. Удалить ваши данные?',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Delete
    elif req[0] == 'del':
        logs(call.from_user.id, 'Перешел на прошлую страницу')
        delete_data(call.from_user.id)
        markup = types.InlineKeyboardMarkup()
        reestablish = types.InlineKeyboardButton("Восстановить", callback_data='res')
        markup.add(reestablish)
        bot.edit_message_text('Данные удалены. Восстановить ваши данные?',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)

    # spelling on
    elif req[0] == 'on':
        logs(call.from_user.id, 'Включил автоматическую проверку текста')
        save_value(call.from_user.id, spelling=True)
        markup = types.InlineKeyboardMarkup()
        spelling_on = types.InlineKeyboardButton("Выключить", callback_data='off')
        markup.add(spelling_on)
        bot.edit_message_text('Автоматическая проверка текста включена',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # spelling off
    elif req[0] == 'off':
        logs(call.from_user.id, 'Выключил автоматическую проверку текста')
        save_value(call.from_user.id, spelling=False)
        markup = types.InlineKeyboardMarkup()
        spelling_of = types.InlineKeyboardButton("Включить", callback_data='on')
        markup.add(spelling_of)
        bot.edit_message_text('Автоматическая проверка текста выключена\n\nОбратите внимание, '
                              'при включение данной функции, ответ от бота возможно будет дольше',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Choice language
    else:
        logs(call.from_user.id, f'Сменил язык на {req[0]}')
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
        # Download file
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # File path
        src = message.document.file_name
        # File translate
        document = document_translate(message.from_user.id, downloaded_file, src)
        if not document:
            logs(message.from_user.id, 'Отправил неподдерживаемый тип файла', type_info='error')
            bot.send_message(message.chat.id, "Неподдерживаемый тип файла")
        # No errors
        else:
            with open("Перевод.txt", 'r', encoding='utf-8') as file:
                bot.send_document(message.chat.id, file)
                logs(message.from_user.id, f'Перевел файл. Количество символов: {len(file.read())}')
            os.remove("Перевод.txt")
        os.remove(src)
    except:
        logs(message.from_user.id, 'Отправил неподдерживаемый файл', type_info='error')
        bot.send_message(message.chat.id, "Неподдерживаемый файл")


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
        logs(message.from_user.id, f'Перевел картинку. Разрешение: {len(message.photo) - 1}. Размер картинки: {message.photo[len(message.photo) - 1].file_size}')
        bot.send_message(message.chat.id, f"Распознанный текст:\n\n{picture['text_recognition']}\n\nПеревод:\n\n{picture['result']}")
        try:
            os.remove("translate.jpg")
        except FileNotFoundError:
            logs(message.from_user.id, 'Ошибка с большим количеством фото одновременно', type_info='error')
    except:
        logs(message.from_user.id, 'Ошибка с переводом', type_info='error')
        bot.send_message(message.chat.id, "Неизвестная ошибка, повторите попытку")


# Message from user for translation
@bot.message_handler(content_types=["text"])
def handle_text(message):
    get_value = Database(message.from_user.id)
    translate = Translate()
    # translation with spell check
    if get_value.get_spelling():
        message_translation = translate.auto_spelling(message.text.strip(), get_value.get_language())
        if message_translation['errors_found']:
            bot.send_message(message.chat.id, message_translation['spelling_text'], parse_mode="Markdown")
        logs(message.from_user.id, f'Перевел текст с авто проверкой.')
        bot.send_message(message.chat.id, message_translation['result'])
    else:
        bot.send_message(message.chat.id, translate.translate(message.text.strip(), get_value.get_language()))
        logs(message.from_user.id, f'Перевел текст без авто проверки.')

bot.polling(none_stop=True, interval=0, timeout=25)


