from telegram import ReplyKeyboardMarkup, KeyboardButton


def pagination_keyboard():
    markup = []
    row = []

    row.append(KeyboardButton('<'))
    row.append(KeyboardButton('>'))

    markup.append(row)
    return ReplyKeyboardMarkup(markup, resize_keyboard=True)
