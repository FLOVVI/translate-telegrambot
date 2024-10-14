import os
import time

from threading import Thread, Event
import telebot
from telebot import types

import config
import analysis

from database import Database
from language import InlineButton
from translator import Translate, AutoSpelling, OtherTranslate


print("Active")
bot = telebot.TeleBot(config.TOKEN)
bot.send_message(config.OWNER_ID, "Сервер запущен")


def edit_message(chat_id, last_message_id, user, event):
    state = 0

    for i in range(300):
        state = state + 1 if state < 3 else 0

        if event.is_set():
            break

        text = f"{'⏳' if state % 2 == 0 else '⌛'}Подождите{'.' * state}"

        bot.edit_message_text(text, chat_id, last_message_id)
        time.sleep(0.7)


# Первое открытие и смена языка
@bot.message_handler(commands=["start", "language"])
def start(message):
    database = Database(message.from_user.id)
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
    if message.from_user.id == config.OWNER_ID:
        bot.send_message(message.chat.id,
                         f'Всего пользователей: {analysis.count_users()}\n{analysis.most_language()[1]}')


# Включить/отключить автоматическую проверку текста
@bot.message_handler(commands=["spelling"])
def switching_spelling(message):
    database = Database(message.from_user.id)
    database.save(spelling=not database.spelling)

    if not database.spelling:
        bot.send_message(message.chat.id, 'Автоматическая проверка текста включена')
    else:
        bot.send_message(message.chat.id, 'Автоматическая проверка текста выключена\n\nОбратите внимание, '
                                          'при включение данной функции, ответ от бота возможно будет дольше')


# Поиск языка
@bot.message_handler(commands=["search"])
def search_language(message):
    database = Database(message.from_user.id)
    database.save(search=not database.search)
    if not database.search:
        bot.send_message(message.chat.id, 'Поиск включен. Пожалуйста напишите язык который вы хотите найти')
    else:
        bot.send_message(message.chat.id, 'Поиск выключен')


# Инлайн режим (Перевод с любого чата) при введенном сообщении
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


# Инлайн режим (Перевод с любого чата) при пустом сообщении
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

    # Страница языка
    if req in ['next', 'back', 'last', 'first', 'menu', 'all']:
        page = database.page

        options = {
            'first': ('Первая страница', 1),
            'last': ('Последняя страница', inline.MAX_PAGE)
        }

        # Выбираем первую или последнюю страницу
        if req in options:
            message, value = options[req]
            bot.answer_callback_query(call.id, message)
            page = value

        if req == 'next':
            page = page + 1 if page < inline.MAX_PAGE else 1

        elif req == 'back':
            page = page - 1 if page > 1 else inline.MAX_PAGE

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


@bot.message_handler(content_types=["text"])
def handler_text(message):
    database = Database(message.from_user.id)
    inline = InlineButton()
    if database.search:
        try:
            bot.send_message(message.chat.id, 'Язык найден:', reply_markup=inline.inline_button(
                inline.language_page(message.from_user.id, message.text.title())))
            database.save(search=False)
        except KeyError:
            bot.send_message(message.chat.id,
                             'Данного языка еще нету в боте. '
                             'Пожалуйста попробуйте снова или напишите /search чтобы выключить поиск.')

    else:
        bot.send_message(message.chat.id, '⏳Подождите')

        # Ожидание выполнения запроса
        event = Event()
        th = Thread(target=edit_message, args=(message.chat.id, message.id + 1, message.from_user.id, event))
        th.start()

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Озвучить", callback_data='voice'))

        translate = Translate()
        auto_spelling = AutoSpelling()

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