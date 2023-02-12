import random
import sqlite3
from config import openai_token
from translator import Translate
from nltk.corpus import wordnet
import openai


def generate_code():
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    repeat = [i[0] for i in sqlite3.connect('translatebot.db').cursor().execute('SELECT code FROM tableone').fetchall()]
    while True:
        code = ''
        # generate a four-digit code
        for i in range(4):
            code += random.choice(letters)
        if code not in repeat:
            break
    return code


class Word:
    def __init__(self):
        self.translate = Translate()
        # session token
        openai.api_key = openai_token
        # chat 3 engine (max)
        self.model_engine = "text-davinci-003"

    @staticmethod
    def word_memorization(word, code):
        # translate the word into English for writing
        word_en = Translate().word_of_the_day_translate(word).title()
        # checking for the existence of such a word
        if wordnet.synsets(word_en):
            with open(f'text_files/{code}', 'a', encoding='utf-8') as file:
                file.write(f'{word_en} ')

    def get_similar(self, word):
        completion = openai.Completion.create(
            engine=self.model_engine,
            prompt=f'write a no more than five words that are often used together with the word {word}',
            max_tokens=3900 - len(word),
            temperature=0.1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return completion.choices[0].text