import random
from translator import Translate
from nltk.corpus import wordnet


def generate_code():
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''
    for i in range(4):
        code += random.choice(letters)
    return code


def word_memorization(word, code):
    # translate the word into English for writing
    word_en = Translate().word_of_the_day_translate(word).title()
    if wordnet.synsets(word_en):
        with open(f'text_files/{code}', 'a', encoding='utf-8') as file:
            file.write(f'{word_en} ')


