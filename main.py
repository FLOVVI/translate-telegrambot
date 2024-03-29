import os
import time
import requests

from threading import Thread, Event
import telebot
from telebot import types

from config import token, server_usage, owner_id
from database import Database
from language import InlineButton
from translator import Translate, AutoSpelling
from other_translate import OtherTranslate
from server import server_load
import analysis as an

print("Active")
bot = telebot.TeleBot(token)


def edit_message(chat_id, last_message_id, user, event):
    state = 0
    database = Database(user)
    server = server_load()

    for i in range(150):
        state = state + 1 if state < 3 else 0

        if event.is_set():
            break

        if int(server.usage_percentage) >= 100:
            text = f"Сервер перегружен. Ответ займет больше времени\n\n" \
                   f"{'⏳' if state % 2 == 0 else '⌛'}Подождите{'.' * state}"
        else:
            text = f"{'⏳' if state % 2 == 0 else '⌛'}Подождите{'.' * state}"

        bot.edit_message_text(text, chat_id, last_message_id)
        time.sleep(0.7)


# Первое открытие и смена языка
@bot.message_handler(commands=["start", "language"])
def start(message):
    database = Database(message.from_user.id)
    if not database.expectation:  # Проверяем выполняются ли другие запросы
        if database.first_start:
            bot.send_message(message.chat.id,
                             'Выберите на какой язык переводить:\n\nДля поиска нужного языка используйте /search',
                             reply_markup=InlineButton().inline_button(database.page))
            database.save(first_start=False)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Сменить язык", callback_data='menu'))
            bot.send_message(message.chat.id, f"Вы переводите на {InlineButton().language_text(database.language)} язык",
                             reply_markup=markup)

@bot.message_handler(commands=["an"])
def analysis(message):
    if message.from_user.id == owner_id:
        bot.send_message(message.chat.id, f'Всего пользователей: {an.count_users()}\n{an.most_language()[1]}')

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
    if not database.expectation:
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
    database.save(upl=False, search=not database.search)
    if not database.expectation:
        if not database.search:
            bot.send_message(message.chat.id, 'Поиск включен. Пожалуйста напишите язык который вы хотите найти')
        else:
            bot.send_message(message.chat.id, 'Поиск выключен')


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(query):
    translate = Translate()
    database = Database(query.from_user.id)
    try:
        bot.answer_inline_query(query.id, [types.InlineQueryResultArticle(
            id='1',
            title=f"Перевожу...",
            description=translate.translate(query.query, database.language),
            input_message_content=types.InputTextMessageContent(message_text=f'{translate.translate(query.query, database.language, prefix=False)}')
        )])
    except Exception:
        pass


@bot.inline_handler(func=lambda query: len(query.query) == 0)
def empty_query(query):
    database = Database(query.from_user.id)
    inline = InlineButton()
    try:
        bot.answer_inline_query(query.id, [types.InlineQueryResultArticle(
            id='1',
            title="Translate",
            description=f'Введите слово для перевода на {inline.language_text(database.language)} язык',
            input_message_content=types.InputTextMessageContent(message_text="А где слово?")
        )])
    except Exception:
        pass


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    database = Database(call.from_user.id)
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

        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id,
                                      reply_markup=inline.inline_button(page))

        database.save(page=page)

    # Озвучка сообщения
    elif req == 'voice':
        # Всплывающее уведомление
        bot.answer_callback_query(call.id, 'Озвучка сообщения')

        # Ожидание выполнения запроса
        bot.send_message(call.message.chat.id, '⏳Подождите')
        event = Event()
        th = Thread(target=edit_message, args=(call.message.chat.id, call.message.id + 1, call.from_user.id, event))
        th.start()

        # Избавляемся от [lang]
        text = call.message.text.split()
        text.remove(text[0])

        try:
            voice = OtherTranslate(call.from_user.id).message_voice(" ".join(text), database.code)

            event.set()  # Заканчиваем запрос
            bot.delete_message(call.message.chat.id, call.message.id + 1)

            with open(voice, 'rb') as audio:
                bot.send_voice(call.message.chat.id, audio)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)

            os.remove(voice)
        except ValueError:
            event.set()  # Заканчиваем запрос
            bot.delete_message(call.message.chat.id, call.message.id + 1)
            bot.send_message(call.message.chat.id, 'Не удалось распознать текст на данном языке')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)

    # Восстановление
    elif req == 'res':
        bot.answer_callback_query(call.id, 'Данные восстановлены')

        Database(call.from_user.id)
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
    database = Database(message.from_user.id)
    if not database.expectation:
        bot.send_message(message.chat.id, '⏳Подождите')
        event = Event()
        th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, message.from_user.id, event))
        th.start()

        file_path = database.code
        file_info = bot.get_file(message.voice.file_id)
        file_download = requests.get(f'https://api.telegram.org/file/bot{token}/{file_info.file_path}')

        with open(f'{file_path}.ogg', 'wb') as file:
            file.write(file_download.content)
        text_recognition, result = OtherTranslate(message.from_user.id).audio_translate(file_path)

        event.set()  # Заканчиваем запрос

        bot.edit_message_text(f"Распознанный текст:\n\n{text_recognition}", message.chat.id, message.id + 1)
        if text_recognition != 'Не удалось распознать текст.':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))

            bot.send_message(message.chat.id, result, reply_markup=markup)

        os.remove(f'{file_path}.wav')


# Перевод документов
@bot.message_handler(content_types=['document'])
def handler_document(message):
    database = Database(message.from_user.id)
    if not database.expectation:
        event = Event()
        # Ожидание выполнения запроса
        bot.send_message(message.chat.id, '⏳Подождите')
        th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, message.from_user.id, event))
        th.start()

        file_path = f'{database.code}.txt'

        try:
            # Скачиваем файл
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Перевод файла
            document = OtherTranslate(message.from_user.id).document_translate(downloaded_file, file_path)
            if not document:
                event.set()
                bot.edit_message_text("Неподдерживаемый тип файла", message.chat.id, message.id + 1)
            # Если нет ошибок
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    bot.send_document(message.chat.id, file)

                event.set()  # Заканчиваем запрос
                bot.delete_message(message.chat.id, message.id + 1)

        except TypeError as e:
            print(e)
            event.set()  # Заканчиваем запрос
            bot.edit_message_text("Неподдерживаемый тип файла", message.chat.id, message.id + 1)

        finally:
            os.remove(file_path)


# Перевод фото
@bot.message_handler(content_types=['photo'])
def handler_photo(message):
    database = Database(message.from_user.id)
    if not database.expectation:
        bot.send_message(message.chat.id, "⏳Подождите")

        # Ожидание выполнения запроса
        event = Event()
        th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, message.from_user.id, event))
        th.start()

        server = server_load()

        if int(server.usage_percentage) < 150 or not server_usage:
            try:

                file_path = f'{database.code}.jpg'

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))

                # Скачиваем файл
                file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                # Переводим файл
                text, result = OtherTranslate(message.from_user.id).picture_translate(downloaded_file, file_path)

                event.set()  # Заканчиваем запрос

                bot.edit_message_text(f"Распознанный текст:\n\n{text}", message.chat.id, message.id + 1)
                bot.send_message(message.chat.id, result, reply_markup=markup)
                try:
                    os.remove(file_path)
                except FileNotFoundError:
                    pass
            except:
                # Заканчиваем запрос
                event.set()

                bot.edit_message_text("Произошла неизвестная ошибка. Повторите попытку", message.chat.id, message.id + 1)
        else:
            # Заканчиваем запрос
            event.set()

            bot.edit_message_text(
                f"Сервер перегружен. Пожалуйста повторите попытку через {Translate().translate(server.resets_text, 'ru', prefix=False)}",
                message.chat.id, message.id + 1)


# Message from user for translation
@bot.message_handler(content_types=["text"])
def handler_text(message):
    database = Database(message.from_user.id)
    if not database.expectation:
        # Поиск включен
        if database.search:
            try:
                bot.send_message(message.chat.id, 'Язык найден:', reply_markup=InlineButton().inline_button(
                    InlineButton().language_page(message.from_user.id, message.text.title())))
                database.save(search=False)
            except KeyError:
                bot.send_message(message.chat.id,
                                 'Данного языка еще нету в боте. Пожалуйста попробуйте снова или напишите /search чтобы выключить поиск.')

        else:
            bot.send_message(message.chat.id, '⏳Подождите')

            # Ожидание выполнения запроса
            event = Event()
            th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, message.from_user.id, event))
            th.start()

            translate = Translate()
            auto_spelling = AutoSpelling()
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))
            if database.spelling:  # Перевод с проверкой орфографии
                # Проверяем ошибки в тексте
                auto_spelling.auto_spelling(message.text.strip(), database.language)
                if auto_spelling.errors_found:  # Если ошибки найдены
                    event.set()  # Заканчиваем запрос
                    bot.edit_message_text(auto_spelling.spelling_text, message.chat.id, message.id + 1,
                                          parse_mode="Markdown")
                    bot.send_message(message.chat.id, auto_spelling.result, reply_markup=markup)
                else:
                    event.set()  # Заканчиваем запрос
                    bot.edit_message_text(auto_spelling.result, message.chat.id, message.id + 1, reply_markup=markup)
            else:  # Обычный перевод
                event.set()  # Заканчиваем запрос
                bot.edit_message_text(translate.translate(message.text.strip(), database.language), message.chat.id,
                                      message.id + 1, reply_markup=markup)


bot.polling(none_stop=True, interval=0, timeout=25)
