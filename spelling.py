from pyaspeller import YandexSpeller


def spelling(text):
    spell = YandexSpeller()
    amended_text = spell.spelled(text)
    amended_text_mas = amended_text.split()
    new_mas = []
    for i in amended_text_mas:
        if i not in text.split():
            new_mas.append(i)

    for i in new_mas:
        index = amended_text_mas.index(i)
        amended_text_mas[index] = f"_{i}_"

    return " ".join(amended_text_mas)
