import sqlite3
import random


class Add:

    @staticmethod
    def generate_code():
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        repeat = [i[0] for i in
                  sqlite3.connect('translatebot.db').cursor().execute('SELECT code FROM main').fetchall()]
        while True:
            code = ''
            # Создаем 4-значный код
            for i in range(4):
                code += random.choice(letters)
            if code not in repeat:
                break
        return code

    @staticmethod
    def search_table():
        # Проверяем наличие таблицы
        connect = sqlite3.connect('translatebot.db')
        cursor = connect.cursor()

        check = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' and name='main'"
        )

        # Если таблицы не существует - создаем её
        if check.fetchone() is None:
            cursor.execute("CREATE TABLE main ("
                           "id INT PRIMARY KEY,"
                           "language STRING,"
                           "spelling BOOLEAN,"
                           "first_start BOOLEAN,"
                           "page INT,"
                           "code STRING,"
                           "search BOOLEAN)"
                           )

    def search_user(self, user):

        # Проверяем наличие пользователя в таблице
        search_connect = sqlite3.connect('translatebot.db')
        search_cursor = search_connect.cursor()

        check = search_cursor.execute(
            "SELECT id FROM main WHERE id = ?", (user,)
        )

        # Если не находим пользователя - создаем его
        if check.fetchone() is None:
            search_cursor.execute("INSERT INTO main VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  (user, "en", False, True, 1, self.generate_code(), False))

        search_connect.commit()


class Database:
    def __init__(self, user, delete=False):
        self.user = user
        if not delete:
            Add().search_user(self.user)

        connect = sqlite3.connect('translatebot.db')
        cursor = connect.cursor()

        self.delete_user = True if cursor.execute("SELECT id FROM main WHERE id = ?",
                                                  (self.user,)).fetchone() is None else False
        if not self.delete_user:
            self.language = cursor.execute(f'SELECT language FROM main WHERE id = {self.user}').fetchone()[0]
            self.spelling = cursor.execute(f'SELECT spelling FROM main WHERE id = {self.user}').fetchone()[0]
            self.first_start = cursor.execute(f'SELECT first_start FROM main WHERE id = {self.user}').fetchone()[0]
            self.page = cursor.execute(f'SELECT page FROM main WHERE id = {self.user}').fetchone()[0]
            self.code = cursor.execute(f'SELECT code FROM main WHERE id = {self.user}').fetchone()[0]
            self.search = cursor.execute(f'SELECT search FROM main WHERE id = {self.user}').fetchone()[0]

    def save(self, **kwargs):
        # Сохранение данных в базу

        connect = sqlite3.connect('translatebot.db')
        cursor = connect.cursor()

        for key, value in kwargs.items():
            cursor.execute(f"UPDATE main SET {key} = ? WHERE id = ?", (value, self.user))
        connect.commit()

    def delete(self):
        # Удаление всех данных из базы

        connect = sqlite3.connect('translatebot.db')
        cursor = connect.cursor()
        cursor.execute("DELETE FROM main WHERE id = ?", (self.user,))
        connect.commit()

Add().search_table()