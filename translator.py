from googletrans import Translator, LANGUAGES
from pyaspeller import YandexSpeller
from language import LANGUAGES_RU


class Translate:

    def __init__(self):
        self.google_translator = Translator()
        self.LANGUAGES = LANGUAGES
        self.spelling = YandexSpeller()
        self.detect = Translator().detect

    def translate(self, text, language) -> str:
        """

        Logic
        ___________
        if the user translates into the language of the text he translated
        then we translate by default into Russian

        Returns
        ___________
        User text translation

        """

        text = "No Text" if text == '' else text

        detect = self.detect(text)

        # Smart translation from Belarusian and Ukrainian is incorrect
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

    def auto_spelling(self, text, language, sorting=True):
        """
        Logic
        ___________
        check the spelling of the text, correct errors

        Returns
        ___________
        translation of the corrected text
        """
        # Corrected text
        spelling_text = self.spelling.spelled(text)
        errors_found = True if spelling_text != text else False
        # Translation of the corrected text
        result = self.translate(spelling_text, language)
        if spelling_text != text and sorting:
            spelling_text = self.spelling_sorting(spelling_text, text)

        return AutoSpelling(errors_found, spelling_text, result)

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


class AutoSpelling:
    def __init__(self, errors_found, spelling_text, result):
        self.errors_found = errors_found
        self.spelling_text = f"В сообщении найдены ошибки. Исправленный текст:\n\n{spelling_text}"
        self.result = result

    def __dict__(self):
        return {'errors_found': self.errors_found,
                'spelling_text': self.spelling_text,
                'result': self.result}


def language_text(language) -> str:
    # .split()[0] for two-word languages (Японский язык)
    return LANGUAGES_RU.get(language).split()[0].title()
