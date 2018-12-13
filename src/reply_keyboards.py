from telegram import ReplyKeyboardMarkup, KeyboardButton
from src.models import ReplyMarkupMessage, current_user

def pagination_keyboard():
    markup = []
    row = []

    row.append(KeyboardButton('<'))
    row.append(KeyboardButton('>'))

    markup.append(row)
    return ReplyKeyboardMarkup(markup, resize_keyboard=True)
