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
            if get_value.get_spelling:
                file.write(translate.auto_spelling(text, get_value.get_language, sorting=False)['result'])
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

    reader = easyocr.Reader(["ru", "en", "uk"])
    result_reader = reader.readtext('translate.jpg', detail=0, paragraph=True)
    if get_value.get_spelling:
        result = translate.auto_spelling(" ".join(result_reader), get_value.get_language, sorting=False)['result']
    else:
        result = translate.translate(" ".join(result_reader), get_value.get_language)

    dictionary = {
        'text_recognition': " ".join(result_reader),
        'result': result,
    }
    return dictionary