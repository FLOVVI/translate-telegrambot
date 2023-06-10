import sqlite3
import random


# Temporary function
def generate_code():
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    repeat = [i[0] for i in sqlite3.connect('translatebot.db').cursor().execute('SELECT code FROM tableone').fetchall()]
    while True:
        code = ''
        # Generate a four-digit code
        for i in range(4):
            code += random.choice(letters)
        if code not in repeat:
            break
    return code


class Database:
    def __init__(self, user, delete=False):
        self.user = user
        if not delete:
            search_user(user)

        get_connect = sqlite3.connect('translatebot.db')
        get_cursor = get_connect.cursor()
        self.get_delete_user = True if get_cursor.execute("SELECT id FROM tableone WHERE id = ?", (self.user,)).fetchone() is None else False
        if not self.get_delete_user:
            self.get_language = get_cursor.execute(f'SELECT language FROM tableone WHERE id = {self.user}').fetchone()[0]
            self.get_spelling = get_cursor.execute(f'SELECT spelling FROM tableone WHERE id = {self.user}').fetchone()[0]
            self.get_first_start = get_cursor.execute(f'SELECT first_start FROM tableone WHERE id = {self.user}').fetchone()[0]
            self.get_page = get_cursor.execute(f'SELECT page FROM tableone WHERE id = {self.user}').fetchone()[0]
            self.get_code = get_cursor.execute(f'SELECT code FROM tableone WHERE id = {self.user}').fetchone()[0]
            self.get_word = get_cursor.execute(f'SELECT word FROM tableone WHERE id = {self.user}').fetchone()[0]
            self.get_search = get_cursor.execute(f'SELECT search FROM tableone WHERE id = {self.user}').fetchone()[0]


def save_value(user, **kwargs):
    save_connect = sqlite3.connect('translatebot.db')
    save_cursor = save_connect.cursor()
    if 'language' in kwargs:
        save_cursor.execute("UPDATE tableone SET language = ? WHERE id = ?", (kwargs['language'], user,))
    if 'spelling' in kwargs:
        save_cursor.execute("UPDATE tableone SET spelling = ? WHERE id = ?", (kwargs['spelling'], user,))
    if 'first_start' in kwargs:
        save_cursor.execute("UPDATE tableone SET first_start = ? WHERE id = ?", (kwargs['first_start'], user,))
    if 'page' in kwargs:
        save_cursor.execute("UPDATE tableone SET page = ? WHERE id = ?", (kwargs['page'], user,))
    if 'code' in kwargs:
        save_cursor.execute("UPDATE tableone SET code = ? WHERE id = ?", (kwargs['code'], user,))
    if 'word' in kwargs:
        save_cursor.execute("UPDATE tableone SET word = ? WHERE id = ?", (kwargs['word'], user,))
    if 'search' in kwargs:
        save_cursor.execute("UPDATE tableone SET search = ? WHERE id = ?", (kwargs['search'], user,))
    save_connect.commit()


def delete_data(user):
    delete_connect = sqlite3.connect('translatebot.db')
    delete_cursor = delete_connect.cursor()
    delete_cursor.execute("DELETE FROM tableone WHERE id = ?", (user,))
    delete_connect.commit()


def search_table():
    search_connect = sqlite3.connect('translatebot.db')
    search_cursor = search_connect.cursor()

    check = search_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' and name='tableone'").fetchone()
    if len(check) == 0:
        search_cursor.execute("CREATE TABLE tableone ("
                              "id INT,"
                              "language STRING,"
                              "spelling BOOLEAN,"
                              "first_start BOOLEAN,"
                              "page INT,"
                              "code STRING,"
                              "word BOOLEAN,"
                              "search BOOLEAN)")


def search_user(user):
    search_connect = sqlite3.connect('translatebot.db')
    search_cursor = search_connect.cursor()

    if search_cursor.execute("SELECT id FROM tableone WHERE id = ?", (user,)).fetchone() is None:
        search_cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (user, "en", False, True, 1, generate_code(), False, False))

    search_connect.commit()


search_table()
