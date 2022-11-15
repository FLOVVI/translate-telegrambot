import sqlite3
from collections import Counter
from googletrans import Translator, LANGUAGES
from telebot import TeleBot
import config as r

bot = TeleBot(r.token)
translator = Translator()
con = sqlite3.connect('translatebot.db')
cursor = con.cursor()


def how_many_people():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT id FROM tableone")
    return f"Всего людей: {len(cursor.fetchall())}"


def frequent_language():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT language FROM tableone")
    occurrence_count = Counter(cursor.fetchall())
    counter = occurrence_count.most_common(1)[0][0]
    counter = counter[0]
    a = LANGUAGES.get(counter)
    result = translator.translate(a.title(), dest="ru")
    if counter != "zh-cn":
        return f"Чаще всего переводят на {result.text} язык"
    else:
        return "Чаще всего переводят на Китайский язык"


def frequent_spelling():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT spelling FROM tableone")
    occurrence_count = Counter(cursor.fetchall())
    counter = occurrence_count.most_common(1)[0][0]
    counter = str(counter)
    counter = counter.replace('(', '')
    counter = counter.replace(')', '')
    counter = counter.replace(",", '')
    if counter == "0":
        return "Чаще всего у пользователей выключена авто проверка орфографии"
    else:
        return "Чаще всего у пользователей включена авто проверка орфографии"


def mailing():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT id from tableone")

    for i in cursor.fetchall():
        i = i[0]

        try:
            bot.send_message(i, "*Первая и последняя рассылка*\n\n",
                             parse_mode="Markdown")
        except:
            print("Бот заблокирован")
