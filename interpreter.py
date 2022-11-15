from googletrans import Translator
import sqlite3
from pyaspeller import YandexSpeller


class lang:
    lang = None
    spelling_TF = None


def translate(user_id, text, TF=True):
    con = sqlite3.connect('translatebot.db')
    cursor = con.cursor()
    cursor.execute("SELECT id FROM tableone WHERE id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO tableone VALUES (?, ?, ?, ?)", (user_id, "en", False, True))
        con.commit()
    cursor.execute(f'SELECT language FROM tableone WHERE id = {user_id}')
    records = cursor.fetchall()
    for i in records:
        lang.lang = (i[0])
    transl = Translator()
    cursor.execute(f'SELECT spelling FROM tableone WHERE id = {user_id}')
    records = cursor.fetchall()
    for i in records:
        lang.spelling_TF = (i[0])
    result = transl.translate(text, dest=lang.lang)
    if lang.spelling_TF and TF:
        spell = YandexSpeller()
        if str(spell.spelled(text)) != str(text):
            if result.src == lang.lang and lang.lang == "ru":
                result = transl.translate(spell.spelled(text), dest="en")
                return f'[en] {result.text}'
            elif result.src == lang.lang:
                result = transl.translate(spell.spelled(text), dest="ru")
                return f'[ru] {result.text}'
            else:
                result = transl.translate(spell.spelled(text), dest=lang.lang)
                return f'[{lang.lang}] {result.text}'
        else:
            if result.src == lang.lang and lang.lang == "ru":
                result = transl.translate(text, dest="en")
                return f'[en] {result.text}'
            elif result.src == lang.lang:
                result = transl.translate(text, dest="ru")
                return f'[ru] {result.text}'
            else:
                result = transl.translate(text, dest=lang.lang)
                return f'[{lang.lang}] {result.text}'

    else:
        if result.src == lang.lang and lang.lang == "ru":
            result = transl.translate(text, dest="en")
            return f'[en] {result.text}'
        elif result.src == lang.lang:
            result = transl.translate(text, dest="ru")
            return f'[ru] {result.text}'
        else:
            result = transl.translate(text, dest=lang.lang)
            return f'[{lang.lang}] {result.text}'