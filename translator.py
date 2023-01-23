from googletrans import Translator, LANGUAGES
from pyaspeller import YandexSpeller


class Translate:

    def __init__(self):
        self.translator = Translator()
        self.LANGUAGES = LANGUAGES
        self.spelling = YandexSpeller()

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
        result = self.translator.translate(text, dest=language)

        # Smart translation from Belarusian and Ukrainian is incorrect
        if language not in ['be', 'uk']:
            if result.src == language:
                if language == "ru":
                    return f'[en] {self.translator.translate(text, dest="en").text}'
                else:
                    return f'[ru] {self.translator.translate(text, dest="ru").text}'
            else:
                return f'[{language}] {result.text}'
        else:
            return f'[{language}] {result.text}'

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
        if spelling_text != text and sorting:
            spelling_text = self.spelling_sorting(spelling_text, text)
        errors_found = True if spelling_text != text else False
        # Translation of the corrected text
        result = self.translate(spelling_text, language)
        return {'result': result,
                'spelling_text': f"В сообщении найдены ошибки. Исправленный текст:\n\n{spelling_text}",
                'errors_found': errors_found}

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


def language_text(language) -> str:
    if language == 'zh-cn':
        return "Китайский"
    elif language == 'hy':
        return "Армянский"
    elif language == 'uk':
        return 'Украинский'
    elif language == 'be':
        return 'Белорусский'
    else:
        # .split()[0] for two-word languages (Японский язык)
        return Translator().translate(LANGUAGES.get(language), dest="ru").text.split()[0].title()


# print(Translate().auto_spelling(input(), "en").spelling_text)