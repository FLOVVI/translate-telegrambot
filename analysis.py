import sqlite3
from collections import Counter

from server import server_load


def statistic():
    return f"Статистика бота:\n\n{number_of_people()}\n{most_language()[1]}\n{most_spelling()}\n{server_load().statistics_text}\n{most_language()[0]}"


def number_of_people():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    return f"Всего пользователей: {len(cursor.execute('SELECT id FROM tableone').fetchall())}"


def most_language():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT language FROM tableone")
    occurrence_count = Counter(cursor.fetchall())
    counter = occurrence_count.most_common()
    popular_language = [i[0][0] for i in counter]
    return popular_language, f"Чаще всего переводят на {counter[0][0][0]} язык"


def most_spelling():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT spelling FROM tableone")
    occurrence_count = Counter(cursor.fetchall())
    counter = str(occurrence_count.most_common(1)[0][0][0])
    if counter == "0":
        return "Чаще всего у пользователей выключена автопроверка орфографии"
    else:
        return "Чаще всего у пользователей включена автопроверка орфографии"