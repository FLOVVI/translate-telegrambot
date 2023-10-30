from googletrans import Translator
from pyaspeller import YandexSpeller


class Translate:
    # Умный перевод эксклюзивно для этого бота

    def __init__(self):
        self.google_translator = Translator()
        self.speller = YandexSpeller()
        self.detect = Translator().detect
        # Переменные для проверки орфографии
        self.errors_found = False
        self.spelling_text = ''
        self.result = ''

    def translate(self, text, language):

        text = "No Text" if text == '' else text.replace('_', ' ')

        detect = self.detect(text)

        # Умный перевод для Беларусского и Украинского языка работает некорректно
        if language not in ['be', 'uk']:
            if detect.lang == language:
                if language == "ru":
                    return f'[en] {self.google_translator.translate(text, dest="en").text}'
                else:
                    return f'[ru] {self.google_translator.translate(text, dest="ru").text}'
            else:
                return f'[{language}] {self.google_translator.translate(text, dest=language).text}'
        else:
            return f'[{language}] {self.google_translator.translate(text, dest=language).text}'


class AutoSpelling(Translate):
    def auto_spelling(self, text, language, sorting=True):

        text = "No Text" if text == '' else text.replace('_', ' ')

        # Corrected text
        spelling_text = self.speller.spelled(text)
        self.errors_found = True if spelling_text != text else False
        # Translation of the corrected text
        self.result = self.translate(spelling_text, language)
        if spelling_text != text and sorting:
            self.spelling_text = f"В сообщении найдены ошибки. Исправленный текст:\n\n{self.spelling_sorting(spelling_text, text)}"

    @staticmethod
    def spelling_sorting(spelling_text, text) -> str:
        corrected_text = spelling_text.split()
        new_mas = []
        for i in corrected_text:
            if i not in text.split():
                new_mas.append(i)
        for i in new_mas:
            corrected_text[corrected_text.index(i)] = f"`{i}`"
        return " ".join(corrected_text)