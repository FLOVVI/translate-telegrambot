import os
import easyocr
import soundfile
import speech_recognition
from gtts import gTTS

from translator import Translate
from database import Database


def document_translate(user, downloaded_file, src):
    get_value = Database(user)
    translate = Translate()

    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    try:
        with open(src, 'r+', encoding='utf-8') as file:
            text = file.read()
        with open("Перевод.txt", 'w+', encoding='utf-8') as file:
            if get_value.get_spelling:
                file.write(translate.auto_spelling(text, get_value.get_language, sorting=False).result)
            else:
                file.write(translate.translate(text, get_value.get_language))
        return True
    except UnicodeDecodeError:
        return False


def picture_translate(user, downloaded_file):
    get_value = Database(user)
    translate = Translate()

    with open("translate.jpg", 'wb') as file:
        file.write(downloaded_file)

    reader = easyocr.Reader(["ru", "en"], gpu=False)
    result_reader = reader.readtext('translate.jpg', detail=0, paragraph=True)
    text = " ".join(result_reader) if len(result_reader) else 'No text'
    if get_value.get_spelling:
        result = translate.auto_spelling(text, get_value.get_language, sorting=False).result
    else:
        result = translate.translate(text, get_value.get_language)

    return PictureTranslate(text, result)


class PictureTranslate:
    def __init__(self, text_recognition, result):
        self.text_recognition = text_recognition
        self.result = result


def message_voice(user, text):
    get_value = Database(user)
    lang = Translate().detect(text).lang

    tts = gTTS(text=text, lang=lang)
    tts.save(f'{get_value.get_code}.ogg')

    return f'{get_value.get_code}.ogg'


def audio_translate(user, audio_id):
    translate = Translate()
    get_value = Database(user)

    language = 'ru-RU' if get_value.get_language == 'en' else 'en-US'

    # Convert
    data, samplerate = soundfile.read(f'{audio_id}.ogg')
    soundfile.write(f'{audio_id}.wav', data, samplerate)
    os.remove(f'{audio_id}.ogg')

    # Recognition
    recognizer = speech_recognition.Recognizer()
    sample = speech_recognition.WavFile(os.path.abspath(f"{audio_id}.wav"))
    with sample as audio:
        recognizer.adjust_for_ambient_noise(audio)
        content = recognizer.record(audio)

        try:
            text_recognition = recognizer.recognize_google(content, language=language)
            result = translate.translate(text_recognition, get_value.get_language)
            return AudioTranslate(text_recognition, result)
        except speech_recognition.UnknownValueError:
            return AudioTranslate('Не удалось распознать текст.')


class AudioTranslate:
    def __init__(self, text_recognition, result=''):
        self.text_recognition = text_recognition
        self.result = result