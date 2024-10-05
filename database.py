import sqlite3
import random, datetime, os
import yadisk
from threading import Thread
import config


class DatabaseCloud:
    def __init__(self, token):
        self.disk = yadisk.YaDisk(token=token)

    def upload(self, user_file, disk_file, remove=True):
        if disk_file in self.listdir() and remove:
            self.remove(disk_file)
        self.disk.upload(user_file, f'database/{disk_file}')

    def download(self, user_file, disk_file):
        os.remove(user_file)
        self.disk.download(f'database/{disk_file}', user_file)

    def listdir(self):
        return [i.name for i in list(self.disk.listdir("/database"))]

    def remove(self, disk_file):
        self.disk.remove(f'database/{disk_file}')


cloud = DatabaseCloud(config.YADISK_TOKEN)
if config.SERVER_USAGE:
    cloud.download('translatebot.db', 'translatebot.db')
    print('База данных установлена.')


# Каждые 3 часа база данных сохраняется в облако
def upload():
    # Получаем текущее время
    now = datetime.datetime.now()
    # Проверяем, время делится на 6?
    if now.hour % 6 == 0:
        try:
            cloud.upload('translatebot.db', 'translatebot.db')
        except:
            cloud.upload('translatebot.db', 'translatebot.db', remove=False)
        print("Данные загружены на облако")


cloud_upload = Thread(target=upload)
cloud_upload.start()


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
    def __init__(self, user):
        self.user = user
        Add().search_user(self.user)

        connect = sqlite3.connect('translatebot.db')
        cursor = connect.cursor()

        self.language = cursor.execute(f'SELECT language FROM main WHERE id = {self.user}').fetchone()[0]
        self.spelling = cursor.execute(f'SELECT spelling FROM main WHERE id = {self.user}').fetchone()[0]
        self.first_start = cursor.execute(f'SELECT first_start FROM main WHERE id = {self.user}').fetchone()[0]
        self.page = cursor.execute(f'SELECT page FROM main WHERE id = {self.user}').fetchone()[0]
        self.code = cursor.execute(f'SELECT code FROM main WHERE id = {self.user}').fetchone()[0]
        self.search = cursor.execute(f'SELECT search FROM main WHERE id = {self.user}').fetchone()[0]

        connect.close()

    def save(self, **kwargs):
        # Сохранение данных в базу

        connect = sqlite3.connect('translatebot.db')
        cursor = connect.cursor()

        key_lst = []

        for key, value in kwargs.items():
            key_lst.append(key)
            cursor.execute(f"UPDATE main SET {key} = ? WHERE id = ?", (value, self.user))
        connect.commit()
        connect.close()