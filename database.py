import sqlite3
import random
import time
from threading import Thread
from database_cloud import DatabaseCloud
from config import yadisk_token, server_usage

cloud = DatabaseCloud(yadisk_token)
if server_usage:
    cloud.download('translatebot.db', 'translatebot.db')
    print('База данных установлена.')


class Data:
    upload_timer = True

data = Data()


def timer():
    data.upload_timer = False
    time.sleep(300)
    data.upload_timer = True


def upload():

    th = Thread(target=timer)
    th.start()

    try:
        cloud.upload('translatebot.db', 'translatebot.db')
    except:
        cloud.upload('translatebot.db', 'translatebot.db', remove=False)


class Add:

    @staticmethod
    def generate_code():
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        repeat = [i[0] for i in
                  sqlite3.connect('translatebot.db').cursor().execute('SELECT code FROM main').fetchall()]
        while True:
            code = ''
            # Создаем 6-и значный код
            for i in range(6):
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
                           "search BOOLEAN,"
                           "expectation BOOLEAN)"
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
            search_cursor.execute("INSERT INTO main VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                  (user, "en", False, True, 1, self.generate_code(), False, False))

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
            self.expectation = cursor.execute(f'SELECT expectation FROM main WHERE id = {self.user}').fetchone()[0]

        connect.close()

    def save(self, upl=True, **kwargs):
        # Сохранение данных в базу

        connect = sqlite3.connect('translatebot.db')
        cursor = connect.cursor()

        key_lst = []

        for key, value in kwargs.items():
            key_lst.append(key)
            cursor.execute(f"UPDATE main SET {key} = ? WHERE id = ?", (value, self.user))
        connect.commit()
        connect.close()

        if server_usage:
            if data.upload_timer and upl:
                print(upl)
                th = Thread(target=upload)
                th.start()

    def delete(self):
        # Удаление всех данных из базы

        connect = sqlite3.connect('translatebot.db')
        cursor = connect.cursor()
        cursor.execute("DELETE FROM main WHERE id = ?", (self.user,))
        connect.commit()
        connect.close()

        if server_usage:
            if data.upload_timer:
                th = Thread(target=upload)
                th.start()


Add().search_table()