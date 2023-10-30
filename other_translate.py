import os
import easyocr
import soundfile
import speech_recognition
from gtts import gTTS

from translator import Translate, AutoSpelling
from database import Database


class OtherTranslate:
    def __init__(self, user):
        self.database = Database(user)
        self.translate = Translate()
        self.auto_spelling = AutoSpelling()

    def document_translate(self, downloaded_file, src):
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        try:
            with open(src, 'r+', encoding='utf-8') as file:
                text = file.read()
            with open("Перевод.txt", 'w+', encoding='utf-8') as file:
                if self.database.spelling:
                    self.auto_spelling.auto_spelling(text, self.database.language, sorting=False)
                    file.write(self.auto_spelling.result)
                else:
                    file.write(self.translate.translate(text, self.database.language))
            return True
        except UnicodeDecodeError:
            return False

    def picture_translate(self, downloaded_file):
        with open("translate.jpg", 'wb') as file:
            file.write(downloaded_file)

        reader = easyocr.Reader(["ru", "en"], gpu=False)
        result_reader = reader.readtext('translate.jpg', detail=0, paragraph=True)
        text = " ".join(result_reader) if len(result_reader) else 'No text'
        if self.database.spelling:
            self.auto_spelling.auto_spelling(text, self.database.language, sorting=False)
            result = self.auto_spelling.result
        else:
            result = self.translate.translate(text, self.database.language)

        return text, result

    def audio_translate(self, audio_id):
        # Конвертируем
        data, samplerate = soundfile.read(f'{audio_id}.ogg')
        soundfile.write(f'{audio_id}.wav', data, samplerate)
        os.remove(f'{audio_id}.ogg')

        # Распознаем
        recognizer = speech_recognition.Recognizer()
        sample = speech_recognition.WavFile(os.path.abspath(f"{audio_id}.wav"))
        with sample as audio:
            recognizer.adjust_for_ambient_noise(audio)
            content = recognizer.record(audio)

            try:
                text_recognition = recognizer.recognize_google(content, language='ru-RU')
                result = self.translate.translate(text_recognition, self.database.language)
                return text_recognition, result
            except speech_recognition.UnknownValueError:
                return 'Не удалось распознать текст.', ''

    def message_voice(self, text):
        lang = self.translate.detect(text).lang

        tts = gTTS(text=text, lang=lang)
        tts.save(f'{self.database.code}.ogg')

        return f'{self.database.code}.ogg'