# -*- coding: utf-8 -*-

import telebot
from telebot import types
import config as r
import os
import sqlite3
from pyaspeller import YandexSpeller
import analysis as an
from spelling import spelling
import easyocr
from interpreter import translate
from googletrans import Translator, LANGUAGES

print("Active")
# database
con = sqlite3.connect('translatebot.db')
cursor = con.cursor()


class Language:
    lang = "en"
    page = 1
    max_page = 3
    spelling_TF: None


lang = Language()

bot = telebot.TeleBot(r.token)
translator = Translator()


# Удаление пользовательских данных
@bot.message_handler(commands=["delete"])
def delete_id(message):
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()

    cursor.execute("SELECT id FROM tableone WHERE id = ?", (message.from_user.id,))
    if cursor.fetchone() is None:
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Восстановить", callback_data='vos')
        markup.add(item1)
        bot.send_message(message.from_user.id, "Восстановить ваши данные?", reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Удалить", callback_data='del')
        markup.add(item1)
        bot.send_message(message.from_user.id, "Удалить ваши данные?", reply_markup=markup)


@bot.message_handler(commands=["id"])
def send_id(message):
    bot.send_message(message.chat.id, message.chat.id)
    print(message.chat.id)


# Анализ по базе данных
@bot.message_handler(commands=["analysis"])
def analysis(message):
    if message.chat.id == r.id_f:
        bot.send_message(message.chat.id,
                         f"{an.how_many_people()}\n\n{an.frequent_language()}\n\n{an.frequent_spelling()}")
    else:
        print("Кто-то знает секретную команду")


# Включение / Отключение авто проверки текста
@bot.message_handler(commands=["spelling"])
def sp(message):
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT id FROM tableone WHERE id = ?", (message.from_user.id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (message.from_user.id, "en", False, True))
        con.commit()
    cursor.execute("SELECT spelling FROM tableone WHERE id = ?", (message.from_user.id,))
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Включить", callback_data='on')
    item2 = types.InlineKeyboardButton("Выключить", callback_data='off')
    records = cursor.fetchall()
    true_or_false = 0
    for i in records:
        true_or_false = i[0]
    if true_or_false == 1:
        markup.add(item2)
        bot.send_message(message.chat.id, 'Автоматическая проверка текста включена',
                         reply_markup=markup)
    if true_or_false == 0:
        markup.add(item1)
        bot.send_message(message.chat.id, 'Автоматическая проверка текста выключена.\n\nОбратите внимание, '
                                          'при включение данной функции, ответ от бота возможно будет дольше',
                         reply_markup=markup)


# Сменить язык
@bot.message_handler(commands=["start", "language"])
def start(message):
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT id FROM tableone WHERE id = ?", (message.from_user.id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (message.from_user.id, "en", False, True))
        con.commit()
    cursor.execute("SELECT first_start FROM tableone WHERE id = ?", (message.from_user.id,))
    first = True
    records = cursor.fetchall()
    for i in records:
        # Первый запуск бота
        first = i[0]
    if first:
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
        item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
        item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
        item4 = types.InlineKeyboardButton("<", callback_data='pg1')
        item5 = types.InlineKeyboardButton(f"{lang.page}/{lang.max_page}", callback_data='pg3')
        item6 = types.InlineKeyboardButton(">", callback_data='pg2')
        markup.add(item1)
        markup.add(item2)
        markup.add(item3)
        markup.add(item4, item5, item6)
        bot.send_message(message.chat.id, 'Выберите на какой язык переводить:', reply_markup=markup)
        cursor.execute("UPDATE tableone SET first_start = ? WHERE id = ?", (False, message.from_user.id,))
        con.commit()
    else:
        cursor.execute("SELECT language FROM tableone WHERE id = ?", (message.from_user.id,))
        records = cursor.fetchall()
        for i in records:
            lang.lang = i[0]
        # Вывод языка
        if lang.lang != "zh-cn":
            result_lang = LANGUAGES.get(lang.lang)
            translate_lang = translator.translate(result_lang, dest="ru")
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
            markup.add(item1)
            bot.send_message(message.chat.id, f'Вы переводите на {translate_lang.text.title()} язык',
                             reply_markup=markup)
        # Вывод китайского языка
        else:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
            markup.add(item1)
            bot.send_message(message.chat.id, 'Вы переводите на Китайский язык', reply_markup=markup)


# Инлайн кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    req = call.data.split('_')

    # Восстановление данных
    if req[0] == 'vos':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "en", False, True))
            con.commit()
            markup = types.InlineKeyboardMarkup()
            item2 = types.InlineKeyboardButton("Удалить", callback_data='del')
            markup.add(item2)
            bot.edit_message_text('Удалить ваши данные?',
                                  reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Удаление данных
    if req[0] == 'del':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            pass
        else:
            cursor.execute("DELETE FROM tableone WHERE id = ?", (call.from_user.id,))
            con.commit()
            markup = types.InlineKeyboardMarkup()
            item2 = types.InlineKeyboardButton("Восстановить", callback_data='vos')
            markup.add(item2)
            bot.edit_message_text('Восстановить ваши данные?',
                                  reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Включение авто проверки текста
    if req[0] == 'on':
        lang.spelling_TF = True
        cursor.execute("UPDATE tableone SET spelling = ? WHERE id = ?", (lang.spelling_TF, call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item2 = types.InlineKeyboardButton("Выключить", callback_data='off')
        markup.add(item2)
        bot.edit_message_text('Автоматическая проверка текста включена',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Выключение авто проверки текста
    if req[0] == 'off':
        lang.spelling_TF = False
        cursor.execute("UPDATE tableone SET spelling = ? WHERE id = ?", (lang.spelling_TF, call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Включить", callback_data='on')
        markup.add(item1)
        bot.edit_message_text('Автоматическая проверка текста выключена\n\nОбратите внимание, '
                              'при включение данной функции, ответ от бота возможно будет дольше',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Список языков при перелистывании назад
    if req[0] == 'pg1':
        if lang.page > 1:
            lang.page -= 1
            if lang.page == 1:
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
                item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
                item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
                item4 = types.InlineKeyboardButton("<", callback_data='pg1')
                item5 = types.InlineKeyboardButton(f"{lang.page}/{lang.max_page}", callback_data='pg3')
                item6 = types.InlineKeyboardButton(">", callback_data='pg2')
                markup.add(item1)
                markup.add(item2)
                markup.add(item3)
                markup.add(item4, item5, item6)
                bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=markup)
            elif lang.page == 2:
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton("Французский", callback_data='pwd5')
                item2 = types.InlineKeyboardButton("Испанский", callback_data='pwd6')
                item3 = types.InlineKeyboardButton("Итальянский", callback_data='pwd7')
                item4 = types.InlineKeyboardButton("<", callback_data='pg1')
                item5 = types.InlineKeyboardButton(f"{lang.page}/{lang.max_page}", callback_data='pg3')
                item6 = types.InlineKeyboardButton(">", callback_data='pg2')
                markup.add(item1)
                markup.add(item2)
                markup.add(item3)
                markup.add(item4, item5, item6)
                bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=markup)
            elif lang.page == 3:
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton("Китайский", callback_data='pwd8')
                item2 = types.InlineKeyboardButton("Японский", callback_data='pwd9')
                item3 = types.InlineKeyboardButton("Корейский", callback_data='pwd10')
                item4 = types.InlineKeyboardButton("<", callback_data='pg1')
                item5 = types.InlineKeyboardButton(f"{lang.page}/{lang.max_page}", callback_data='pg3')
                item6 = types.InlineKeyboardButton(">", callback_data='pg2')
                markup.add(item1)
                markup.add(item2)
                markup.add(item3)
                markup.add(item4, item5, item6)
                bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=markup)
    # Список языков при перелистывании вперед
    if req[0] == 'pg2':
        if lang.page < lang.max_page:
            lang.page += 1
            if lang.page == 1:
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
                item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
                item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
                item4 = types.InlineKeyboardButton("<", callback_data='pg1')
                item5 = types.InlineKeyboardButton(f"{lang.page}/{lang.max_page}", callback_data='pg3')
                item6 = types.InlineKeyboardButton(">", callback_data='pg2')
                markup.add(item1)
                markup.add(item2)
                markup.add(item3)
                markup.add(item4, item5, item6)
                bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=markup)
            elif lang.page == 2:
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton("Французский", callback_data='pwd5')
                item2 = types.InlineKeyboardButton("Испанский", callback_data='pwd6')
                item3 = types.InlineKeyboardButton("Итальянский", callback_data='pwd7')
                item4 = types.InlineKeyboardButton("<", callback_data='pg1')
                item5 = types.InlineKeyboardButton(f"{lang.page}/{lang.max_page}", callback_data='pg3')
                item6 = types.InlineKeyboardButton(">", callback_data='pg2')
                markup.add(item1)
                markup.add(item2)
                markup.add(item3)
                markup.add(item4, item5, item6)
                bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=markup)
            elif lang.page == 3:
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton("Китайский", callback_data='pwd8')
                item2 = types.InlineKeyboardButton("Японский", callback_data='pwd9')
                item3 = types.InlineKeyboardButton("Корейский", callback_data='pwd10')
                item4 = types.InlineKeyboardButton("<", callback_data='pg1')
                item5 = types.InlineKeyboardButton(f"{lang.page}/{lang.max_page}", callback_data='pg3')
                item6 = types.InlineKeyboardButton(">", callback_data='pg2')
                markup.add(item1)
                markup.add(item2)
                markup.add(item3)
                markup.add(item4, item5, item6)
                bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=markup)
    # Полный список доступных языков
    if req[0] == 'pg3':
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
        item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
        item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
        item4 = types.InlineKeyboardButton("Французский", callback_data='pwd5')
        item5 = types.InlineKeyboardButton("Испанский", callback_data='pwd6')
        item6 = types.InlineKeyboardButton("Итальянский", callback_data='pwd7')
        item7 = types.InlineKeyboardButton("Китайский", callback_data='pwd8')
        item8 = types.InlineKeyboardButton("Японский", callback_data='pwd9')
        item9 = types.InlineKeyboardButton("Корейский", callback_data='pwd10')
        item0 = types.InlineKeyboardButton("Назад", callback_data='pwd3')
        markup.add(item1, item2, item3)
        markup.add(item4, item5, item6)
        markup.add(item7, item8, item9)
        markup.add(item0)
        bot.edit_message_text('Выберите на какой язык переводить:',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Перевод на Русский язык
    if req[0] == 'pwd1':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "ru", False, True))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("ru", call.from_user.id,))
        con.commit()

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text('Вы переводите на Русский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Перевод на Английский язык
    if req[0] == 'pwd2':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "en", False, True))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("en", call.from_user.id,))
        con.commit()

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text('Вы переводите на Английский язык',
                              reply_markup=markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
    # Меню выбора языка
    if req[0] == 'pwd3':
        lang.page = 1
        if lang.page == 1:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
            item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
            item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
            item4 = types.InlineKeyboardButton("<", callback_data='pg1')
            item5 = types.InlineKeyboardButton(f"{lang.page}/{lang.max_page}", callback_data='pg3')
            item6 = types.InlineKeyboardButton(">", callback_data='pg2')
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            markup.add(item4, item5, item6)
            bot.edit_message_text('Выберите на какой язык переводить:',
                                  reply_markup=markup,
                                  chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Перевод на Немецкий язык
    if req[0] == 'pwd4':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "de", False, True))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("de", call.from_user.id,))
        con.commit()

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text('Вы переводите на Немецкий язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Перевод на Французский язык
    if req[0] == 'pwd5':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "fr", False, True))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("fr", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text('Вы переводите на Французский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Перевод на Испанский язык
    if req[0] == 'pwd6':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "es", False, True))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("es", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text('Вы переводите на Испанский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Перевод на Итальянский язык
    if req[0] == 'pwd7':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "it", False, True))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("it", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text('Вы переводите на Итальянский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Перевод на Китайский язык
    if req[0] == 'pwd8':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "zh-cn", False, True))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("zh-cn", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text('Вы переводите на Китайский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Перевод на Японский язык
    if req[0] == 'pwd9':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "ja", False, True))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("ja", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text('Вы переводите на Японский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    # Перевод на Корейский язык
    if req[0] == 'pwd10':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (call.from_user.id, "ko", False, True))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("ko", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text('Вы переводите на Корейский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)


# Перевод документов
@bot.message_handler(content_types=['document'])
def handle_document(message):

    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT id FROM tableone WHERE id = ?", (message.from_user.id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (message.from_user.id, "en", False, True))
        con.commit()
    cursor.execute(f'SELECT language FROM tableone WHERE id ={message.chat.id}')
    records = cursor.fetchall()
    for i in records:
        lang.lang = (i[0])
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = message.document.file_name
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    with open(src, 'r+', encoding='utf-8') as file:
        text = file.read()
        if len(text) > 10000:
            bot.send_message(message.chat.id, "Файл слишком большой, придется подождать...")
    with open("Перевод.txt", 'w+', encoding='utf-8') as file:
        file.write(translate(message.from_user.id, text, TF=False))
    with open("Перевод.txt", 'r', encoding='utf-8') as file:
        bot.send_document(message.chat.id, file)
    os.remove(src)
    os.remove("Перевод.txt")


# Перевод фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "Подождите...")
    file_info = bot.get_file(message.photo[2].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("translate.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT id FROM tableone WHERE id = ?", (message.from_user.id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (message.from_user.id, "en", False, True))
        con.commit()
    cursor.execute(f'SELECT language FROM tableone WHERE id ={message.chat.id}')
    records = cursor.fetchall()
    for i in records:
        lang.lang = (i[0])
    reader = easyocr.Reader(["ru", "en", "uk"])
    result = reader.readtext('translate.jpg', detail=0, paragraph=True)
    text_recognition = " ".join(result)
    cursor.execute(f'SELECT spelling FROM tableone WHERE id = {message.chat.id}')
    records = cursor.fetchall()
    for i in records:
        lang.spelling_TF = (i[0])
    spell = YandexSpeller()
    if lang.spelling_TF:
        if str(spell.spelled(text_recognition)) != str(text_recognition):
            bot.send_message(message.chat.id, "В распознанном сообщении найдены ошибки. Исправленный текст: \n\n"
                                              f"{spelling(text_recognition)}", parse_mode="Markdown")
    bot.send_message(message.chat.id, f"Распознанный текст:\n\n{spell.spelled(text_recognition)}\n\n"
                                      f"Перевод:\n\n{translate(message.from_user.id, text_recognition)}")
    os.remove("translate.jpg")


# Сообщение от пользователя
@bot.message_handler(content_types=["text"])
def handle_text(message):
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    # Анализируем отправленное сообщение от пользователя
    ms = message.text.split()
    if ms[0] == "#sendall" and message.from_user.id == r.id_f:
        ms.remove(ms[0])
        cursor.execute("SELECT id FROM tableone")
        records = cursor.fetchall()
        for i in records:
            i = i[0]
            try:
                print(f"Отправил сообщение: [{i}]")
                bot.send_message(i, " ".join(ms))
            except:
                cursor.execute("DELETE FROM tableone WHERE id = ?", (i,))

    else:
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (message.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (message.from_user.id, "en", False, True))
            con.commit()
        cursor.execute(f'SELECT spelling FROM tableone WHERE id = {message.chat.id}')
        records = cursor.fetchall()
        for i in records:
            lang.spelling_TF = (i[0])

        if lang.spelling_TF:
            spell = YandexSpeller()
            if str(spell.spelled(message.text)) != str(message.text):
                bot.send_message(message.chat.id, "В введенном сообщении найдены ошибки. Исправленный текст: \n\n"
                                                  f"{spelling(message.text)}", parse_mode="Markdown")
        bot.send_message(message.chat.id, translate(message.from_user.id, message.text))

try:
    bot.polling(none_stop=True, interval=0, timeout=20)
except:
    print("Ошибка подключения")
    bot.send_message(r.id_f, "Ошибка подключения. Перезапустите бота.")

# Текстовый документ с логикой бота (Логика.txt)