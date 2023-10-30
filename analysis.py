import sqlite3
from collections import Counter


def most_language():
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT language FROM main")
    occurrence_count = Counter(cursor.fetchall())
    counter = occurrence_count.most_common()
    popular_language = [i[0][0] for i in counter]
    return popular_language, f"Чаще всего переводят на {counter[0][0][0]} язык"