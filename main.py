import os
import time
import requests

from threading import Thread, Event
import telebot
from telebot import types

from config import token, owner_id
from database import *
from translator import Translate
from language import inline_button, language_page, max_page, language_text
from analysis import statistic
from other_translate import document_translate, picture_translate, message_voice, audio_translate
from server import server_load

print("Active")
bot = telebot.TeleBot(token)


def edit_message(chat_id, last_message_id, event):
    state = 0
    for i in range(150):
        if state < 3:
            state += 1
        else:
            state = 0

        if event.is_set():
            break

        text = f"{'⏳' if state % 2 == 0 else '⌛'}Подождите{'.' * state}"

        bot.edit_message_text(text, chat_id, last_message_id)
        time.sleep(0.75)


# First launch and language change
@bot.message_handler(commands=["start", "language"])
def start(message):
    get_value = Database(message.from_user.id)
    if get_value.get_first_start:
        bot.send_message(message.chat.id, 'Выберите на какой язык переводить:\n\nДля поиска нужного языка используйте /search', reply_markup=inline_button(get_value.get_page))
        save_value(message.from_user.id, first_start=False)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Сменить язык", callback_data='menu'))
        bot.send_message(message.chat.id, f"Вы переводите на {language_text(get_value.get_language)} язык", reply_markup=markup)


# Deleting user data
@bot.message_handler(commands=["delete"])
def delete_id(message):
    get_value = Database(message.from_user.id, delete=True)
    markup = types.InlineKeyboardMarkup()
    if get_value.get_delete_user:
        markup.add(types.InlineKeyboardButton("Восстановить", callback_data='res'))
        bot.send_message(message.from_user.id, "Восстановить ваши данные?", reply_markup=markup)
    else:
        markup.add(types.InlineKeyboardButton("Удалить", callback_data='del'))
        bot.send_message(message.from_user.id, "Удалить ваши данные?", reply_markup=markup)


# Enable / Disable auto text checking
@bot.message_handler(commands=["spelling"])
def switching_spelling(message):
    get_value = Database(message.from_user.id)
    markup = types.InlineKeyboardMarkup()

    if get_value.get_spelling:
        markup.add(types.InlineKeyboardButton("Выключить", callback_data='off'))
        bot.send_message(message.chat.id, 'Автоматическая проверка текста включена', reply_markup=markup)
    else:
        markup.add(types.InlineKeyboardButton("Включить", callback_data='on'))
        bot.send_message(message.chat.id, 'Автоматическая проверка текста выключена.\n\nОбратите внимание, '
                                          'при включение данной функции, ответ от бота возможно будет дольше',
                         reply_markup=markup)


@bot.message_handler(commands=["search"])
def search_language(message):
    get_value = Database(message.from_user.id)
    save_value(message.from_user.id, search=not get_value.get_search)
    if not get_value.get_search:
        bot.send_message(message.chat.id, 'Поиск включен. Пожалуйста напишите язык который вы хотите найти')
    else:
        bot.send_message(message.chat.id, 'Поиск выключен')


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
    search_user(call.from_user.id)
    req = call.data.split('_')
    get_value = Database(call.from_user.id)

    if req[0] in ['next', 'back', 'last', 'first', 'menu', 'all']:
        page = get_value.get_page

        options = {
            'first': ('Первая страница', 1),
            'last': ('Последняя страница', max_page)
        }

        if req[0] in options:
            message, value = options[req[0]]
            bot.answer_callback_query(call.id, message)
            page = value

        if req[0] == 'next':
            bot.answer_callback_query(call.id, 'Следующая страница')
            page = page + 1 if page < max_page else 1

        if req[0] == 'back':
            bot.answer_callback_query(call.id, 'Предыдущая страница')
            page = page - 1 if page > 1 else max_page

        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inline_button(page))

        save_value(call.from_user.id, page=page)

    # Message voice
    elif req[0] == 'voice':
        # Pop-up notification
        bot.answer_callback_query(call.id, 'Озвучка сообщения')

        # Waiting for query execution
        bot.send_message(call.message.chat.id, '⏳Подождите')
        event = Event()
        th = Thread(target=edit_message, args=(call.message.chat.id, call.message.id + 1, event))
        th.start()

        # Get rid of [lang]
        text = call.message.text.split()
        text.remove(text[0])
        try:
            voice = message_voice(call.from_user.id, " ".join(text))

            # End of query execution
            event.set()
            bot.delete_message(call.message.chat.id, call.message.id + 1)

            with open(voice, 'rb') as audio:
                bot.send_voice(call.message.chat.id, audio)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)

            os.remove(voice)
        except ValueError:
            event.set()
            bot.delete_message(call.message.chat.id, call.message.id + 1)
            bot.send_message(call.message.chat.id, 'Не удалось распознать текст на данном языке')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)

    # Reestablish
    elif req[0] == 'res':
        bot.answer_callback_query(call.id, 'Данные восстановлены')

        # Get_Database automatically restores data
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Удалить", callback_data='del'))
        bot.edit_message_text('Данные восстановлены. Удалить ваши данные?',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Delete
    elif req[0] == 'del':
        bot.answer_callback_query(call.id, 'Данные удалены')

        delete_data(call.from_user.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Восстановить", callback_data='res'))
        bot.edit_message_text('Данные удалены. Восстановить ваши данные?',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)

    # spelling on
    elif req[0] == 'on':
        bot.answer_callback_query(call.id, 'Включено')

        save_value(call.from_user.id, spelling=True)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Выключить", callback_data='off'))
        bot.edit_message_text('Автоматическая проверка текста включена',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # spelling off
    elif req[0] == 'off':
        bot.answer_callback_query(call.id, 'Выключено')

        save_value(call.from_user.id, spelling=False)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Включить", callback_data='on'))
        bot.edit_message_text('Автоматическая проверка текста выключена\n\nОбратите внимание, '
                              'при включение данной функции, ответ от бота возможно будет дольше',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Choice language
    else:
        bot.answer_callback_query(call.id, f'Перевод на {language_text(req[0])}')

        save_value(call.from_user.id, language=req[0])
        markup = types.InlineKeyboardMarkup()
        change_language = types.InlineKeyboardButton("Сменить язык", callback_data='menu')
        markup.add(change_language)
        bot.edit_message_text(f'Вы переводите на {language_text(req[0])} язык',
                              reply_markup=markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id)


# Audio Translate
@bot.message_handler(content_types=['voice'])
def handler_audio(message):
    # Waiting for query execution
    bot.send_message(message.chat.id, '⏳Подождите')
    event = Event()
    th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, event))
    th.start()

    get_value = Database(message.from_user.id)

    file_info = bot.get_file(message.voice.file_id)
    file_download = requests.get(f'https://api.telegram.org/file/bot{token}/{file_info.file_path}')

    with open(f'{get_value.get_code}.ogg', 'wb') as file:
        file.write(file_download.content)
    text_recognition, result = audio_translate(message.from_user.id, get_value.get_code)

    # End of query execution
    event.set()

    bot.edit_message_text(f"Распознанный текст:\n\n{text_recognition}", message.chat.id, message.id + 1)
    if text_recognition != 'Не удалось распознать текст.':

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))

        bot.send_message(message.chat.id, result, reply_markup=markup)

    os.remove(f'{get_value.get_code}.wav')


# Document Translate
@bot.message_handler(content_types=['document'])
def handler_document(message):
    try:
        # Waiting for query execution
        bot.send_message(message.chat.id, '⏳Подождите')
        event = Event()
        th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, event))
        th.start()

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

        # End of query execution
        event.set()
        bot.delete_message(message.chat.id, message.id + 1)

    except:
        bot.edit_message_text("Неподдерживаемый тип файла", message.chat.id, message.id + 1)


# Picture translate
@bot.message_handler(content_types=['photo'])
def handler_photo(message):

    # Waiting for query execution
    bot.send_message(message.chat.id, "⏳Подождите")
    event = Event()
    th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, event))
    th.start()

    server = server_load()

    if int(server.usage_percentage) < 50:
        try:

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))

            # Download file
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            # File translate
            text_recognition, result = picture_translate(message.from_user.id, downloaded_file)

            # End of query execution
            event.set()

            bot.edit_message_text(f"Распознанный текст:\n\n{text_recognition}", message.chat.id, message.id + 1)
            bot.send_message(message.chat.id, result, reply_markup=markup)
            try:
                os.remove("translate.jpg")
            except FileNotFoundError:
                pass
        except:
            # End of query execution
            event.set()

            bot.edit_message_text("Произошла неизвестная ошибка. Повторите попытку", message.chat.id, message.id + 1)
    else:
        # End of query execution
        event.set()

        bot.edit_message_text(f"Сервер перегружен. Пожалуйста повторите попытку через {Translate().translate(server.resets_text,'ru')[5:]}", message.chat.id, message.id + 1)


# Message from user for translation
@bot.message_handler(content_types=["text"])
def handler_text(message):
    get_value = Database(message.from_user.id)

    if get_value.get_search:
        try:
            bot.send_message(message.chat.id, 'Язык найден:', reply_markup=inline_button(language_page(message.from_user.id, message.text.title())))
            save_value(message.from_user.id, search=False)
        except KeyError:
            bot.send_message(message.chat.id, 'Данного языка еще нету в боте. Пожалуйста попробуйте снова или напишите /search чтобы выключить поиск.')

    else:
        bot.send_message(message.chat.id, 'Подождите...')
        translate = Translate()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))
        # translation with spell check
        if get_value.get_spelling:
            # checking for errors in the text
            errors_found, spelling_text, result = translate.auto_spelling(message.text.strip(), get_value.get_language)
            if errors_found:
                # if errors are found
                bot.edit_message_text(spelling_text, message.chat.id, message.id + 1, parse_mode="Markdown")
                bot.send_message(message.chat.id, result, reply_markup=markup)
            else:
                bot.edit_message_text(result, message.chat.id, message.id + 1, reply_markup=markup)
        else:
            bot.edit_message_text(translate.translate(message.text.strip(), get_value.get_language), message.chat.id, message.id + 1, reply_markup=markup)


bot.polling(none_stop=True, interval=0, timeout=25)