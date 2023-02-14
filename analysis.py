import sqlite3
from collections import Counter
from translator import language_text
from cpu import get_cpu_usage

con = sqlite3.connect('translatebot.db')
cursor = con.cursor()


def statistic():
    return f"Статистика бота:\n\n{how_many_people()}\n{frequent_language()}\n{frequent_spelling()}\n{get_cpu_usage()}"


def how_many_people():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    return f"Всего людей: {len(cursor.execute('SELECT id FROM tableone').fetchall())}"


def frequent_language():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT language FROM tableone")
    occurrence_count = Counter(cursor.fetchall())
    counter = occurrence_count.most_common(1)[0][0][0]
    return f"Чаще всего переводят на {language_text(counter)} язык"


def frequent_spelling():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT spelling FROM tableone")
    occurrence_count = Counter(cursor.fetchall())
    counter = str(occurrence_count.most_common(1)[0][0][0])
    if counter == "0":
        return "Чаще всего у пользователей выключена авто проверка орфографии"
    else:
        return "Чаще всего у пользователей включена авто проверка орфографии"