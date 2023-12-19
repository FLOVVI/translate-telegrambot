import os

import easyocr
import soundfile
import speech_recognition
from gtts import gTTS
from PIL import Image

from translator import Translate, AutoSpelling
from database import Database


class OtherTranslate:
    def __init__(self, user):
        self.database = Database(user)
        self.translate = Translate()
        self.auto_spelling = AutoSpelling()

    def document_translate(self, downloaded_file, file_path):
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        try:
            with open(file_path, 'r+', encoding='utf-8') as file:
                text = file.read()
            with open(file_path, 'w+', encoding='utf-8') as file:
                if self.database.spelling:
                    self.auto_spelling.auto_spelling(text, self.database.language, sorting=False)
                    file.write(self.auto_spelling.result)
                else:
                    file.write(self.translate.translate(text, self.database.language))
            return True
        except UnicodeDecodeError:
            return False

    def picture_translate(self, downloaded_file, file_path):

        with open(file_path, 'wb') as file:
            file.write(downloaded_file)

        image = Image.open(file_path)
        image = image.convert('L')
        image.save(file_path)

        reader = easyocr.Reader(["ru", "en"], gpu=False)
        result_reader = reader.readtext(file_path, detail=0, paragraph=True)
        text = " ".join(result_reader) if len(result_reader) else 'Текст не найден'
        if self.database.spelling:
            self.auto_spelling.auto_spelling(text, self.database.language, sorting=False)
            result = self.auto_spelling.result
        else:
            result = self.translate.translate(text, self.database.language)

        return text, result

    def audio_translate(self, file_path):
        # Конвертируем
        data, samplerate = soundfile.read(f'{file_path}.ogg')
        soundfile.write(f'{file_path}.wav', data, samplerate)
        os.remove(f'{file_path}.ogg')

        # Распознаем
        recognizer = speech_recognition.Recognizer()
        sample = speech_recognition.WavFile(os.path.abspath(f"{file_path}.wav"))
        with sample as audio:
            recognizer.adjust_for_ambient_noise(audio)
            content = recognizer.record(audio)

            try:
                text_recognition = recognizer.recognize_google(content, language='ru-RU')
                result = self.translate.translate(text_recognition, self.database.language)
                return text_recognition, result
            except speech_recognition.UnknownValueError:
                return 'Не удалось распознать текст.', ''

    def message_voice(self, text, file_path):
        lang = self.translate.detect(text).lang

        tts = gTTS(text=text, lang=lang)
        tts.save(f'{file_path}.ogg')

        return f'{file_path}.ogg'