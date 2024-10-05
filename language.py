from telebot import types
from database import Database
from analysis import most_language


class Language:
    def __init__(self):
        self.MAX_PAGE = 35
        self.LANGUAGES_RU = {'af': 'Африканский', 'sq': 'Албанский', 'am': 'Амхарский', 'ar': 'Арабский', 'hy': 'Армянский', 'az': 'Азербайджанский', 'eu': 'Баскский', 'be': 'Белорусский', 'bn': 'Бенгальский', 'bs': 'Боснийский', 'bg': 'Болгарский', 'ca': 'Каталонский', 'ceb': 'Себуанский', 'ny': 'Чичевский', 'zh-cn': 'Китайский Упрощенный', 'zh-tw': 'Китайский Традиционный', 'co': 'Корсиканский', 'hr': 'Хорватский', 'cs': 'Чешский', 'da': 'Датский', 'nl': 'Голландский', 'en': 'Английский', 'eo': 'Эсперантский', 'et': 'Эстонский', 'tl': 'Филиппинский', 'fi': 'Финский', 'fr': 'Французский', 'fy': 'Фризский', 'gl': 'Галицкий', 'ka': 'Грузинский', 'de': 'Немецкий', 'el': 'Греческий', 'gu': 'Гуджаратский', 'ht': 'Гаитянский', 'ha': 'Хауский', 'haw': 'Гавайский', 'iw': 'Ивритский', 'hi': 'Хинди', 'hmn': 'Хмонгский', 'hu': 'Венгерский', 'is': 'Исландский', 'ig': 'Игбийский', 'id': 'Индонезийский', 'ga': 'Ирландский', 'it': 'Итальянский', 'ja': 'Японский', 'jw': 'Яванский', 'kn': 'Каннадский', 'kk': 'Казахский', 'km': 'Кхмерский', 'ko': 'Корейский', 'ku': 'Курдский', 'ky': 'Кыргизский', 'lo': 'Лаоский', 'la': 'Латинский', 'lv': 'Латышский', 'lt': 'Литовский', 'lb': 'Люксембургский', 'mk': 'Македонский', 'mg': 'Малагасийский', 'ms': 'Малайский', 'ml': 'Малаяламский', 'mt': 'Мальтийский', 'mi': 'Маорийский', 'mr': 'Маратхийский', 'mn': 'Монгольский', 'my': 'Мьянма', 'ne': 'Непальский', 'no': 'Норвежский', 'or': 'Одиа', 'ps': 'Паш', 'fa': 'Персидский', 'pl': 'Лак', 'pt': 'Португальский', 'pa': 'Пенджаби', 'ro': 'Румынский', 'ru': 'Русский', 'sm': 'Самоанский', 'gd': 'Шотландцы Гэльские', 'sr': 'Сербский', 'sn': 'Шона', 'sd': 'Синди', 'si': 'Лион', 'sk': 'Словацкий', 'sl': 'Словенский', 'so': 'Сомалийский', 'es': 'Испанский', 'su': 'Сунданец', 'sw': 'Суахили', 'sv': 'Шведский', 'tg': 'Таджикский', 'ta': 'Тамильский', 'te': 'Телугу', 'th': 'Тайский', 'tr': 'Турецкий', 'uk': 'Украинский', 'ur': 'Урду', 'ug': 'Уйгурский', 'uz': 'Узбекcкий', 'vi': 'Вьетнамский', 'cy': 'Валлийский', 'xh': 'Коса', 'yi': 'Идиш', 'yo': 'Йоруба', 'zu': 'Зулу'}
        self.LANGUAGES_RU_REVERSED = {'Африканский': 'af', 'Албанский': 'sq', 'Амхарский': 'am', 'Арабский': 'ar', 'Армянский': 'hy', 'Азербайджанский': 'az', 'Баскский': 'eu', 'Белорусский': 'be', 'Бенгальский': 'bn', 'Боснийский': 'bs', 'Болгарский': 'bg', 'Каталонский': 'ca', 'Себуанский': 'ceb', 'Чичевский': 'ny', 'Китайский': 'zh-cn', 'Китайский Традиционный': 'zh-tw', 'Корсиканский': 'co', 'Хорватский': 'hr', 'Чешский': 'cs', 'Датский': 'da', 'Голландский': 'nl', 'Английский': 'en', 'Эсперантский': 'eo', 'Эстонский': 'et', 'Филиппинский': 'tl', 'Финский': 'fi', 'Французский': 'fr', 'Фризский': 'fy', 'Галицкий': 'gl', 'Грузинский': 'ka', 'Немецкий': 'de', 'Греческий': 'el', 'Гуджаратский': 'gu', 'Гаитянский': 'ht', 'Хауский': 'ha', 'Гавайский': 'haw', 'Ивритский': 'iw', 'Хинди': 'hi', 'Хмонгский': 'hmn', 'Венгерский': 'hu', 'Исландский': 'is', 'Игбийский': 'ig', 'Индонезийский': 'id', 'Ирландский': 'ga', 'Итальянский': 'it', 'Японский': 'ja', 'Яванский': 'jw', 'Каннадский': 'kn', 'Казахский': 'kk', 'Кхмерский': 'km', 'Корейский': 'ko', 'Курдский': 'ku', 'Кыргизский': 'ky', 'Лаоский': 'lo', 'Латинский': 'la', 'Латышский': 'lv', 'Литовский': 'lt', 'Люксембургский': 'lb', 'Македонский': 'mk', 'Малагасийский': 'mg', 'Малайский': 'ms', 'Малаяламский': 'ml', 'Мальтийский': 'mt', 'Маорийский': 'mi', 'Маратхийский': 'mr', 'Монгольский': 'mn', 'Мьянма': 'my', 'Непальский': 'ne', 'Норвежский': 'no', 'Одиа': 'or', 'Паш': 'ps', 'Персидский': 'fa', 'Лак': 'pl', 'Португальский': 'pt', 'Пенджаби': 'pa', 'Румынский': 'ro', 'Русский': 'ru', 'Самоанский': 'sm', 'Шотландцы Гэльские': 'gd', 'Сербский': 'sr', 'Шона': 'sn', 'Синди': 'sd', 'Лион': 'si', 'Словацкий': 'sk', 'Словенский': 'sl', 'Сомалийский': 'so', 'Испанский': 'es', 'Сунданец': 'su', 'Суахили': 'sw', 'Шведский': 'sv', 'Таджикский': 'tg', 'Тамильский': 'ta', 'Телугу': 'te', 'Тайский': 'th', 'Турецкий': 'tr', 'Украинский': 'uk', 'Урду': 'ur', 'Уйгур': 'ug', 'Узбек': 'uz', 'Вьетнамский': 'vi', 'Валлийский': 'cy', 'Коса': 'xh', 'Идиш': 'yi', 'Йоруба': 'yo', 'Зулу': 'zu'}
        self.LANGUAGES_KEY = ['ru', 'en', 'de', 'uk', 'be', 'kk', 'fr', 'it', 'es', 'zh-cn', 'ja', 'ko', 'af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'bn', 'bs', 'bg', 'ca', 'ceb', 'ny', 'zh-tw', 'co', 'hr', 'cs', 'da', 'nl', 'eo', 'et', 'tl', 'fi', 'fy', 'gl', 'ka', 'el', 'gu', 'ht', 'ha', 'haw', 'iw', 'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'jw', 'kn', 'km', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'or', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'sm', 'gd', 'sr', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu']

        for i in list(reversed(most_language()[0])):
            self.LANGUAGES_KEY.remove(i)
            self.LANGUAGES_KEY.insert(0, i)

    def language_page(self, user, language):

        key = self.LANGUAGES_RU_REVERSED[language]

        for i in range(len(self.LANGUAGES_KEY) // 3):
            if key in self.LANGUAGES_KEY[i * 3:(i + 1) * 3]:
                Database(user).save(page=i + 1)
                return i + 1

    def language_text(self, language):
        # .split()[0] для языков состоящих из двух слов (Японский язык)
        return self.LANGUAGES_RU[language].split()[0].title()


class InlineButton(Language):
    def inline_button(self, page):
        markup = types.InlineKeyboardMarkup(row_width=5)

        # on every page
        first_page = types.InlineKeyboardButton("<<", callback_data='first')
        previous_page = types.InlineKeyboardButton("<", callback_data='back')
        which_page = types.InlineKeyboardButton(f"{page}/{self.MAX_PAGE}", callback_data='all')
        next_page = types.InlineKeyboardButton(">", callback_data='next')
        last_page = types.InlineKeyboardButton(">>", callback_data='last')

        markup.add(types.InlineKeyboardButton(self.LANGUAGES_RU[self.LANGUAGES_KEY[(1 + (page - 1) * 3) - 1]], callback_data=self.LANGUAGES_KEY[(1 + (page - 1) * 3) - 1]))
        markup.add(types.InlineKeyboardButton(self.LANGUAGES_RU[self.LANGUAGES_KEY[(2 + (page - 1) * 3) - 1]], callback_data=self.LANGUAGES_KEY[(2 + (page - 1) * 3) - 1]))
        markup.add(types.InlineKeyboardButton(self.LANGUAGES_RU[self.LANGUAGES_KEY[(3 + (page - 1) * 3) - 1]], callback_data=self.LANGUAGES_KEY[(3 + (page - 1) * 3) - 1]))

        markup.add(first_page, previous_page, which_page, next_page, last_page)

        return markup