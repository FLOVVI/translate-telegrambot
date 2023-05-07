from telebot import types

max_page = 6


def inline_button(page):
    markup = types.InlineKeyboardMarkup(row_width=5)

    # on every page
    very_previous_page = types.InlineKeyboardButton("<<", callback_data='veryback')
    previous_page = types.InlineKeyboardButton("<", callback_data='back')
    which_page = types.InlineKeyboardButton(f"{page}/{max_page}", callback_data='all')
    next_page = types.InlineKeyboardButton(">", callback_data='next')
    very_next_page = types.InlineKeyboardButton(">>", callback_data='verynext')

    if page == 1:
        # page 1
        markup.add(types.InlineKeyboardButton("Русский", callback_data='ru'))
        markup.add(types.InlineKeyboardButton("Английский", callback_data='en'))
        markup.add(types.InlineKeyboardButton("Немецкий", callback_data='de'))

    if page == 2:
        # page 2
        markup.add(types.InlineKeyboardButton("Белорусский", callback_data='be'))
        markup.add(types.InlineKeyboardButton("Украинский", callback_data='uk'))
        markup.add(types.InlineKeyboardButton("Казахский", callback_data='kk'))

    if page == 3:
        # page 3
        markup.add(types.InlineKeyboardButton("Французский", callback_data='fr'))
        markup.add(types.InlineKeyboardButton("Испанский", callback_data='es'))
        markup.add(types.InlineKeyboardButton("Итальянский", callback_data='it'))

    if page == 4:
        # page 4
        markup.add(types.InlineKeyboardButton("Китайский", callback_data='zh-cn'))
        markup.add(types.InlineKeyboardButton("Японский", callback_data='ja'))
        markup.add(types.InlineKeyboardButton("Корейский", callback_data='ko'))

    if page == 5:
        # page 5
        markup.add(types.InlineKeyboardButton("Хорватский", callback_data='hr'))
        markup.add(types.InlineKeyboardButton("Сербский", callback_data='sr'))
        markup.add(types.InlineKeyboardButton("Болгарский", callback_data='bg'))

    if page == 6:
        # page 6
        markup.add(types.InlineKeyboardButton("Албанский", callback_data='sq'))
        markup.add(types.InlineKeyboardButton("Каталанский", callback_data='ca'))
        markup.add(types.InlineKeyboardButton("Голландский", callback_data='nl'))

    markup.add(very_previous_page, previous_page, which_page, next_page, very_next_page)

    return markup


def language_page(language):
    language_page_dict = {
        "Русский": 1,
        "Английски": 1,
        "Немецкий": 1,
        "Белорусский": 2,
        "Украинский": 2,
        "Казахский": 2,
        "Французский": 3,
        "Испанский": 3,
        "Итальянский": 3,
        "Китайский": 4,
        "Японский": 4,
        "Корейский": 4,
        "Хорватский": 5,
        "Сербский": 5,
        "Болгарский": 5,
        "Албанский": 6,
        "Каталанский": 6,
        "Голландский": 6,
    }

    return language_page_dict[language]