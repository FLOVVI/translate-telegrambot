import sqlite3


class Database:
    def __init__(self, user, delete=False):
        self.user = user
        if not delete:
            search_user(user)
        # Other
        ...

    def get_language(self) -> str:
        get_connect = sqlite3.connect('translatebot.db')
        get_cursor = get_connect.cursor()
        return get_cursor.execute(f'SELECT language FROM tableone WHERE id = {self.user}').fetchone()[0]

    def get_spelling(self) -> bool:
        get_connect = sqlite3.connect('translatebot.db')
        get_cursor = get_connect.cursor()
        return get_cursor.execute(f'SELECT spelling FROM tableone WHERE id = {self.user}').fetchone()[0]

    def get_first_start(self) -> bool:
        get_connect = sqlite3.connect('translatebot.db')
        get_cursor = get_connect.cursor()
        return get_cursor.execute("SELECT first_start FROM tableone WHERE id = ?", (self.user,)).fetchone()[0]

    def get_page(self) -> int:
        get_connect = sqlite3.connect('translatebot.db')
        get_cursor = get_connect.cursor()
        return get_cursor.execute("SELECT page FROM tableone WHERE id = ?", (self.user,)).fetchone()[0]

    def get_delete_user(self) -> bool:
        delete_con = sqlite3.connect('translatebot.db')
        delete_cursor = delete_con.cursor()
        user_check = delete_cursor.execute("SELECT id FROM tableone WHERE id = ?", (self.user,)).fetchone()
        # Check if user profile is deleted
        return True if user_check is None else False


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
    save_connect.commit()


def delete_data(user):
    delete_connect = sqlite3.connect('translatebot.db')
    delete_cursor = delete_connect.cursor()
    delete_cursor.execute("DELETE FROM tableone WHERE id = ?", (user,))
    delete_connect.commit()


def search_table():
    search_connect = sqlite3.connect('translatebot.db')
    search_cursor = search_connect.cursor()

    if len(search_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' and name='tableone'").fetchall()) == 0:
        search_cursor.execute(
            "CREATE TABLE tableone(id INT, language TEXT, spelling BOOLEAN, first_start BOOLEAN, page INT)")


def search_user(user):
    search_connect = sqlite3.connect('translatebot.db')
    search_cursor = search_connect.cursor()

    if search_cursor.execute("SELECT id FROM tableone WHERE id = ?", (user,)).fetchone() is None:
        search_cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?, ?)", (user, "en", False, True, 1))

    search_connect.commit()
