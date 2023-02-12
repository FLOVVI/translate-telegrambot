import random
from translator import Translate
from nltk.corpus import wordnet


def generate_code():
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    repeat = [i[0] for i in sqlite3.connect('translatebot.db').cursor().execute('SELECT code FROM tableone').fetchall()]
    while True:
        code = ''
        for i in range(4):
            code += random.choice(letters)
        if code not in repeat:
            break
    return code


def word_memorization(word, code):
    # translate the word into English for writing
    word_en = Translate().word_of_the_day_translate(word).title()
    # checking for the existence of such a word
    if wordnet.synsets(word_en):
        with open(f'text_files/{code}', 'a', encoding='utf-8') as file:
            file.write(f'{word_en} ')

