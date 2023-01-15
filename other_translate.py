import easyocr

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
            if get_value.get_spelling():
                file.write(translate.auto_spelling(text, get_value.get_language(), sorting=False)['result'])
            else:
                file.write(translate.translate(text, get_value.get_language()))
        return True
    except UnicodeDecodeError:
        return False


def picture_translate(user, downloaded_file):
    get_value = Database(user)
    translate = Translate()

    with open("translate.jpg", 'wb') as file:
        file.write(downloaded_file)

    reader = easyocr.Reader(["ru", "en", "uk"])
    result = reader.readtext('translate.jpg', detail=0, paragraph=True)
    dictionary = {
        'text_recognition': " ".join(result),
        'result': None,
    }
    if get_value.get_spelling():
        dictionary['result'] = translate.auto_spelling(dictionary["text_recognition"], get_value.get_language(), sorting=False)['result']
    else:
        dictionary['result'] = translate.translate(dictionary["text_recognition"], get_value.get_language())
    return dictionary