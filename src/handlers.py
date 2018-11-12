from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import itertools
from src.models import User, Message, Tag

MAX_BUTTONS_IN_ROW=2

def start(bot, update):
    tags = ', '.join([tag.title for tag in _current_user(update).tags])
    bot.send_message(chat_id=update.message.chat_id,
                     text=tags)

def add_tag(bot, update, args):
    Tag.create(user=_current_user(update),
               title=args[0])

def bookmark(bot, update):
    _resend_message_with_markup(bot, update)
    #bot.send_message(chat_id=update.message.chat_id,
    #                 text=update.message.text)

def _resend_message_with_markup(bot, update):
    # !!! Only 8 messages in a row available
    # !!! Any number of rows available(at high numbers breaks shit)
    bot.send_message(chat_id=update.message.chat_id,
                     text=update.message.caption,
                     reply_markup=_build_markup(update))

def _current_user(update):
    telegram_user = update.message.from_user
    user, _ = User.get_or_create(
                id=telegram_user.id,
                defaults={'first_name': telegram_user.first_name,
                          'last_name': telegram_user.last_name,
                          'username': telegram_user.username})
    return user

def _build_markup(update):
    tags = _current_user(update).popular_tags()
    markup = InlineKeyboardMarkup(
        [InlineKeyboardButton(tags[0].title, callback_data=tags[0].title),
         InlineKeyboardButton(tags[1].title, callback_data=tags[1].title)]
        [InlineKeyboardButton(tags[2].title, callback_data=tags[2].title)]
    )
