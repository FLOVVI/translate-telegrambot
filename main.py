import os
import time
import requests

from threading import Thread, Event
import telebot
from telebot import types

from config import token
from database import Database
from language import InlineButton
from translator import Translate, AutoSpelling
from other_translate import OtherTranslate
from server import server_load

print("Active")
bot = telebot.TeleBot(token)


def edit_message(chat_id, last_message_id, event):
    state = 0
    for i in range(150):
        state = state + 1 if state < 3 else 0

        if event.is_set():
            break

        text = f"{'⏳' if state % 2 == 0 else '⌛'}Подождите{'.' * state}"

        bot.edit_message_text(text, chat_id, last_message_id)
        time.sleep(0.75)


# Первое открытие и смена языка
@bot.message_handler(commands=["start", "language"])
def start(message):
    database = Database(message.from_user.id)

    if database.first_start:
        bot.send_message(message.chat.id, 'Выберите на какой язык переводить:\n\nДля поиска нужного языка используйте /search', reply_markup=InlineButton().inline_button(database.page))
        database.save(first_start=False)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Сменить язык", callback_data='menu'))
        bot.send_message(message.chat.id, f"Вы переводите на {InlineButton().language_text(database.language)} язык", reply_markup=markup)


# Удаление данных пользователя
@bot.message_handler(commands=["delete"])
def delete_id(message):
    database = Database(message.from_user.id, delete=True)
    markup = types.InlineKeyboardMarkup()
    if database.delete_user:
        markup.add(types.InlineKeyboardButton("Восстановить", callback_data='res'))
        bot.send_message(message.from_user.id, "Восстановить ваши данные?", reply_markup=markup)
    else:
        markup.add(types.InlineKeyboardButton("Удалить", callback_data='del'))
        bot.send_message(message.from_user.id, "Удалить ваши данные?", reply_markup=markup)


# Включить/отключить автоматическую проверку текста
@bot.message_handler(commands=["spelling"])
def switching_spelling(message):
    database = Database(message.from_user.id)
    markup = types.InlineKeyboardMarkup()

    if database.spelling:
        markup.add(types.InlineKeyboardButton("Выключить", callback_data='off'))
        bot.send_message(message.chat.id, 'Автоматическая проверка текста включена', reply_markup=markup)
    else:
        markup.add(types.InlineKeyboardButton("Включить", callback_data='on'))
        bot.send_message(message.chat.id, 'Автоматическая проверка текста выключена', reply_markup=markup)


# Поиск языка
@bot.message_handler(commands=["search"])
def search_language(message):
    database = Database(message.from_user.id)
    database.save(search=not database.search)
    if not database.search:
        bot.send_message(message.chat.id, 'Поиск включен. Пожалуйста напишите язык который вы хотите найти')
    else:
        bot.send_message(message.chat.id, 'Поиск выключен')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    database = Database(call.from_user.id)
    database.search_user(call.from_user.id)
    inline = InlineButton()
    req = call.data

    if req in ['next', 'back', 'last', 'first', 'menu', 'all']:
        page = database.page

        options = {
            'first': ('Первая страница', 1),
            'last': ('Последняя страница', inline.max_page)
        }

        # Выбираем первую или последнюю страницу
        if req in options:
            message, value = options[req]
            bot.answer_callback_query(call.id, message)
            page = value

        if req == 'next':
            bot.answer_callback_query(call.id, 'Следующая страница')
            page = page + 1 if page < inline.max_page else 1

        if req == 'back':
            bot.answer_callback_query(call.id, 'Предыдущая страница')
            page = page - 1 if page > 1 else inline.max_page

        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inline.inline_button(page))

        database.save(page=page)

    # Озвучка сообщения
    elif req == 'voice':
        # Всплывающее уведомление
        bot.answer_callback_query(call.id, 'Озвучка сообщения')

        # Ожидание выполнения запроса
        bot.send_message(call.message.chat.id, '⏳Подождите')
        event = Event()
        th = Thread(target=edit_message, args=(call.message.chat.id, call.message.id + 1, event))
        th.start()

        # Избавляемся от [lang]
        text = call.message.text.split()
        text.remove(text[0])

        try:
            voice = OtherTranslate.message_voice(call.from_user.id, " ".join(text))

            # Заканчиваем запрос
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

    # Восстановление
    elif req == 'res':
        bot.answer_callback_query(call.id, 'Данные восстановлены')

        database.search_user(call.from_user.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Удалить", callback_data='del'))
        bot.edit_message_text('Данные восстановлены. Удалить ваши данные?',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Удаление
    elif req == 'del':
        bot.answer_callback_query(call.id, 'Данные удалены')

        database.delete()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Восстановить", callback_data='res'))
        bot.edit_message_text('Данные удалены. Восстановить ваши данные?',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)

    # spelling on
    elif req == 'on':
        bot.answer_callback_query(call.id, 'Включено')

        database.save(spelling=True)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Выключить", callback_data='off'))
        bot.edit_message_text('Автоматическая проверка текста включена',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # spelling off
    elif req == 'off':
        bot.answer_callback_query(call.id, 'Выключено')

        database.save(spelling=False)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Включить", callback_data='on'))
        bot.edit_message_text('Автоматическая проверка текста выключена\n\nОбратите внимание, '
                              'при включение данной функции, ответ от бота возможно будет дольше',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Выбор языка
    else:
        bot.answer_callback_query(call.id, f'Перевод на {inline.language_text(req)}')

        database.save(language=req)
        markup = types.InlineKeyboardMarkup()
        change_language = types.InlineKeyboardButton("Сменить язык", callback_data='menu')
        markup.add(change_language)
        bot.edit_message_text(f'Вы переводите на {inline.language_text(req)} язык',
                              reply_markup=markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id)


# Перевод голосовых сообщений
@bot.message_handler(content_types=['voice'])
def handler_audio(message):
    # Ожидание выполнения запроса
    bot.send_message(message.chat.id, '⏳Подождите')
    event = Event()
    th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, event))
    th.start()

    database = Database(message.from_user.id)

    file_info = bot.get_file(message.voice.file_id)
    file_download = requests.get(f'https://api.telegram.org/file/bot{token}/{file_info.file_path}')

    with open(f'{database.code}.ogg', 'wb') as file:
        file.write(file_download.content)
    text_recognition, result = OtherTranslate(message.from_user.id).audio_translate(database.code)

    # Заканчиваем запрос
    event.set()

    bot.edit_message_text(f"Распознанный текст:\n\n{text_recognition}", message.chat.id, message.id + 1)
    if text_recognition != 'Не удалось распознать текст.':

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))

        bot.send_message(message.chat.id, result, reply_markup=markup)

    os.remove(f'{database.code}.wav')


# Перевод документов
@bot.message_handler(content_types=['document'])
def handler_document(message):

    event = Event()
    # Ожидание выполнения запроса
    bot.send_message(message.chat.id, '⏳Подождите')
    th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, event))
    th.start()

    try:
        # Скачиваем файл
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Ссылка на файл
        src = message.document.file_name
        # Перевод файла
        document = OtherTranslate(message.from_user.id).document_translate(downloaded_file, src)
        if not document:
            event.set()
            bot.edit_message_text("Неподдерживаемый тип файла", message.chat.id, message.id + 1)
        # Если нет ошибок
        else:
            with open("Перевод.txt", 'r', encoding='utf-8') as file:
                bot.send_document(message.chat.id, file)
            os.remove("Перевод.txt")
        os.remove(src)

        # Заканчиваем запрос
        event.set()
        bot.delete_message(message.chat.id, message.id + 1)

    except:
        event.set()
        bot.edit_message_text("Неподдерживаемый тип файла", message.chat.id, message.id + 1)


# Перевод фото
@bot.message_handler(content_types=['photo'])
def handler_photo(message):

    # Ожидание выполнения запроса
    bot.send_message(message.chat.id, "⏳Подождите")
    event = Event()
    th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, event))
    th.start()

    server = server_load()

    if int(server.usage_percentage) < 65:
        try:

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))

            # Скачиваем файл
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            # Переводим файл
            text, result = OtherTranslate(message.from_user.id,).picture_translate(downloaded_file)

            # Заканчиваем запрос
            event.set()

            bot.edit_message_text(f"Распознанный текст:\n\n{text}", message.chat.id, message.id + 1)
            bot.send_message(message.chat.id, result, reply_markup=markup)
            try:
                os.remove("translate.jpg")
            except FileNotFoundError:
                pass
        except:
            # Заканчиваем запрос
            event.set()

            bot.edit_message_text("Произошла неизвестная ошибка. Повторите попытку", message.chat.id, message.id + 1)
    else:
        # Заканчиваем запрос
        event.set()

        bot.edit_message_text(f"Сервер перегружен. Пожалуйста повторите попытку через {Translate().translate(server.resets_text,'ru')[5:]}", message.chat.id, message.id + 1)


# Message from user for translation
@bot.message_handler(content_types=["text"])
def handler_text(message):
    database = Database(message.from_user.id)

    if database.search:
        try:
            bot.send_message(message.chat.id, 'Язык найден:', reply_markup=InlineButton().inline_button(InlineButton().language_page(message.from_user.id, message.text.title())))
            database.save(search=False)
        except KeyError:
            bot.send_message(message.chat.id, 'Данного языка еще нету в боте. Пожалуйста попробуйте снова или напишите /search чтобы выключить поиск.')

    else:
        bot.send_message(message.chat.id, 'Подождите...')
        translate = Translate()
        auto_spelling = AutoSpelling()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))
        # Перевод с проверкой орфографии
        if database.spelling:
            # Проверяем ошибки в тексте
            auto_spelling.auto_spelling(message.text.strip(), database.language)
            if auto_spelling.errors_found:
                # Если ошибки найдены
                bot.edit_message_text(auto_spelling.spelling_text, message.chat.id, message.id + 1, parse_mode="Markdown")
                bot.send_message(message.chat.id, auto_spelling.result, reply_markup=markup)
            else:
                bot.edit_message_text(auto_spelling.result, message.chat.id, message.id + 1, reply_markup=markup)
        else:
            # Обычный перевод
            bot.edit_message_text(translate.translate(message.text.strip(), database.language), message.chat.id, message.id + 1, reply_markup=markup)
bot.polling(none_stop=True, interval=0, timeout=25)