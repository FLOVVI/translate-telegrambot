from googletrans import Translator
import telebot
from telebot import types
import config as r
import os
import sqlite3
from pyaspeller import YandexSpeller
import analysis as an
print("Active")
con = sqlite3.connect('translatebot.db')
cursor = con.cursor()


class Language:
    lang = "en"
    page = 1
    max_page = 3
    spelling_TF: None


l = Language()
bot = telebot.TeleBot(r.token)


@bot.message_handler(commands=["analysis"])
def spelling(message):
    if message.chat.id == 1162855035:
        an.removing_duplicate_id()
        bot.send_message(message.chat.id,
                         f"{an.how_many_people()}\n\n{an.frequent_language()}\n\n{an.frequent_spelling()}")
    else:
        print("Кто-то знает секретную команду")


@bot.message_handler(commands=["spelling"])
def spelling(message):
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
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


@bot.message_handler(commands=["start", "language"])
def start(message):
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT id FROM tableone WHERE id = ?", (message.from_user.id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (message.from_user.id, "en", False))
        con.commit()

    l.page = 1
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
    item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
    item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
    item4 = types.InlineKeyboardButton("<", callback_data='pg1')
    item5 = types.InlineKeyboardButton(f"{l.page}/{l.max_page}", callback_data='pg3')
    item6 = types.InlineKeyboardButton(f">", callback_data='pg2')
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    markup.add(item4, item5, item6)
    bot.send_message(message.chat.id, f'Выберите на какой язык переводить:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    req = call.data.split('_')

    if req[0] == 'on':
        l.spelling_TF = True
        markup = types.InlineKeyboardMarkup()
        item2 = types.InlineKeyboardButton("Выключить", callback_data='off')
        markup.add(item2)
        bot.edit_message_text(f'Автоматическая проверка текста включена',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        cursor.execute("UPDATE tableone SET spelling = ? WHERE id = ?", (l.spelling_TF, call.from_user.id,))
        con.commit()

    if req[0] == 'off':
        l.spelling_TF = False
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Включить", callback_data='on')
        markup.add(item1)
        bot.edit_message_text(f'Автоматическая проверка текста выключена\n\nОбратите внимание, '
                              'при включение данной функции, ответ от бота возможно будет дольше',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        cursor.execute("UPDATE tableone SET spelling = ? WHERE id = ?", (l.spelling_TF, call.from_user.id,))
        con.commit()

    if req[0] == 'pg1':
        if l.page > 1:
            l.page -= 1
        if l.page == 1:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
            item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
            item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
            item4 = types.InlineKeyboardButton("<", callback_data='pg1')
            item5 = types.InlineKeyboardButton(f"{l.page}/{l.max_page}", callback_data='pg3')
            item6 = types.InlineKeyboardButton(f">", callback_data='pg2')
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            markup.add(item4, item5, item6)
            bot.edit_message_text(f'Выберите нa какой язык переводить:',
                                  reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif l.page == 2:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Французский", callback_data='pwd5')
            item2 = types.InlineKeyboardButton("Испанский", callback_data='pwd6')
            item3 = types.InlineKeyboardButton("Итальянский", callback_data='pwd7')
            item4 = types.InlineKeyboardButton("<", callback_data='pg1')
            item5 = types.InlineKeyboardButton(f"{l.page}/{l.max_page}", callback_data='pg3')
            item6 = types.InlineKeyboardButton(f">", callback_data='pg2')
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            markup.add(item4, item5, item6)
            bot.edit_message_text(f'Выберите на какoй язык переводить:',
                                  reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif l.page == 3:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Китайский", callback_data='pwd8')
            item2 = types.InlineKeyboardButton("Японский", callback_data='pwd9')
            item3 = types.InlineKeyboardButton("Корейский", callback_data='pwd10')
            item4 = types.InlineKeyboardButton("<", callback_data='pg1')
            item5 = types.InlineKeyboardButton(f"{l.page}/{l.max_page}", callback_data='pg3')
            item6 = types.InlineKeyboardButton(f">", callback_data='pg2')
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            markup.add(item4, item5, item6)
            bot.edit_message_text(f'Выберите на какой язык переводить:',
                                  reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pg2':
        if l.page < l.max_page:
            l.page += 1
        if l.page == 1:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
            item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
            item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
            item4 = types.InlineKeyboardButton("<", callback_data='pg1')
            item5 = types.InlineKeyboardButton(f"{l.page}/{l.max_page}", callback_data='pg3')
            item6 = types.InlineKeyboardButton(f">", callback_data='pg2')
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            markup.add(item4, item5, item6)
            bot.edit_message_text(f'Выберите на какой язык переводить:',
                                  reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif l.page == 2:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Французский", callback_data='pwd5')
            item2 = types.InlineKeyboardButton("Испанский", callback_data='pwd6')
            item3 = types.InlineKeyboardButton("Итальянский", callback_data='pwd7')
            item4 = types.InlineKeyboardButton("<", callback_data='pg1')
            item5 = types.InlineKeyboardButton(f"{l.page}/{l.max_page}", callback_data='pg3')
            item6 = types.InlineKeyboardButton(f">", callback_data='pg2')
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            markup.add(item4, item5, item6)
            bot.edit_message_text(f'Выберите на какой язык переводить:',
                                  reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif l.page == 3:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Китайский", callback_data='pwd8')
            item2 = types.InlineKeyboardButton("Японский", callback_data='pwd9')
            item3 = types.InlineKeyboardButton("Корейский", callback_data='pwd10')
            item4 = types.InlineKeyboardButton("<", callback_data='pg1')
            item5 = types.InlineKeyboardButton(f"{l.page}/{l.max_page}", callback_data='pg3')
            item6 = types.InlineKeyboardButton(f">", callback_data='pg2')
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            markup.add(item4, item5, item6)
            bot.edit_message_text(f'Выберите на какой язык переводить:',
                                  reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
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
        bot.edit_message_text(f'Выберите на какой язык переводить:',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd1':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (call.from_user.id, "ru", False))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("ru", call.from_user.id,))
        con.commit()

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Русский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd2':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (call.from_user.id, "en", False))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("en", call.from_user.id,))
        con.commit()

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Английский язык',
                              reply_markup=markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
    if req[0] == 'pwd3':
        l.page = 1
        if l.page == 1:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Русский", callback_data='pwd1')
            item2 = types.InlineKeyboardButton("Английский", callback_data='pwd2')
            item3 = types.InlineKeyboardButton("Немецкий", callback_data='pwd4')
            item4 = types.InlineKeyboardButton("<", callback_data='pg1')
            item5 = types.InlineKeyboardButton(f"{l.page}/{l.max_page}", callback_data='pg3')
            item6 = types.InlineKeyboardButton(f">", callback_data='pg2')
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            markup.add(item4, item5, item6)
            bot.edit_message_text(f'Выберите на какой язык переводить:',
                                  reply_markup=markup,
                                  chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd4':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (call.from_user.id, "de", False))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("de", call.from_user.id,))
        con.commit()

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Немецкий язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd5':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (call.from_user.id, "fr", False))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("fr", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Французский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd6':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (call.from_user.id, "es", False))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("es", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Испанский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd7':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (call.from_user.id, "it", False))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("it", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Итальянский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd8':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (call.from_user.id, "zh-cn", False))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("zh-cn", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Китайский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd9':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (call.from_user.id, "ja", False))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("ja", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Японский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    if req[0] == 'pwd10':
        cursor.execute("SELECT id FROM tableone WHERE id = ?", (call.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tableone VALUES (?, ?, ?)", (call.from_user.id, "ko", False))
        else:
            cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", ("ko", call.from_user.id,))
        con.commit()
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сменить язык", callback_data='pwd3')
        markup.add(item1)
        bot.edit_message_text(f'Вы переводите на Корейский язык',
                              reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        con = sqlite3.connect('translatebot.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT language FROM tableone WHERE id ={message.chat.id}')
        records = cursor.fetchall()
        for i in records:
            l.lang = (i[0])
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        with open(src, 'r+', encoding='utf-8') as file:
            text = file.read()
            if len(text) > 10000:
                bot.send_message(message.chat.id, "Файл слишком большой, придется подождать...")
            translator = Translator()
            result = translator.translate(text, dest=l.lang)
        with open("Перевод.txt", 'w+', encoding='utf-8') as file:
            file.write(result.text)
        with open("Перевод.txt", 'r', encoding='utf-8') as file:
            bot.send_document(message.chat.id, file)
        try:
            os.remove(src)
            os.remove("Перевод.txt")
        except:
            pass
    except:
        bot.send_message(message.chat.id, "Произошла ошибка, пожалуйста отправьте документ еще раз")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "Перевод фото временно недоступен. Ведутся технический работы")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    try:
        con = sqlite3.connect('translatebot.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT language FROM tableone WHERE id = {message.chat.id}')
        records = cursor.fetchall()
        for i in records:
            l.lang = (i[0])
        translator = Translator()
        cursor.execute(f'SELECT spelling FROM tableone WHERE id = {message.chat.id}')
        records = cursor.fetchall()
        for i in records:
            l.spelling_TF = (i[0])
        result = translator.translate(message.text, dest=l.lang)
        if l.spelling_TF:
            try:
                spell = YandexSpeller()
                if str(spell.spelled(message.text)) != str(message.text):
                    bot.send_message(message.chat.id, "В введенном сообщении найдены ошибки. "
                                                      f"Исправленный текст: \n\n{spell.spelled(message.text)}")
                    if result.src == l.lang and l.lang == "ru":
                        result = translator.translate(spell.spelled(message.text), dest="en")
                        bot.send_message(message.chat.id, f'[en] {result.text}')
                    elif result.src == l.lang:
                        result = translator.translate(spell.spelled(message.text), dest="ru")
                        bot.send_message(message.chat.id, f'[ru] {result.text}')
                    else:
                        result = translator.translate(spell.spelled(message.text), dest=l.lang)
                        bot.send_message(message.chat.id, f'[{l.lang}] {result.text}')
                else:
                    if result.src == l.lang and l.lang == "ru":
                        result = translator.translate(message.text, dest="en")
                        bot.send_message(message.chat.id, f'[en] {result.text}')
                    elif result.src == l.lang:
                        result = translator.translate(message.text, dest="ru")
                        bot.send_message(message.chat.id, f'[ru] {result.text}')
                    else:
                        result = translator.translate(message.text, dest=l.lang)
                        bot.send_message(message.chat.id, f'[{l.lang}] {result.text}')
            except:
                if result.src == l.lang and l.lang == "ru":
                    result = translator.translate(message.text, dest="en")
                    bot.send_message(message.chat.id, f'[en] {result.text}')
                elif result.src == l.lang:
                    result = translator.translate(message.text, dest="ru")
                    bot.send_message(message.chat.id, f'[ru] {result.text}')
                else:
                    result = translator.translate(message.text, dest=l.lang)
                    bot.send_message(message.chat.id, f'[{l.lang}] {result.text}')
        else:
            if result.src == l.lang and l.lang == "ru":
                result = translator.translate(message.text, dest="en")
                bot.send_message(message.chat.id, f'[en] {result.text}')
            elif result.src == l.lang:
                result = translator.translate(message.text, dest="ru")
                bot.send_message(message.chat.id, f'[ru] {result.text}')
            else:
                result = translator.translate(message.text, dest=l.lang)
                bot.send_message(message.chat.id, f'[{l.lang}] {result.text}')
    except:
        bot.send_message(message.chat.id, "Произошла ошибка, пожалуйста повторите попытку")


bot.polling(none_stop=True, interval=0)
