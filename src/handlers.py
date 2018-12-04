from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from src.models import User, Tag, Message

MAX_BUTTONS_IN_ROW = 2

def start(bot, update):
    tags = ', '.join([tag.title for tag in _current_user(update.message.from_user).tags])
    if tags:
        bot.send_message(chat_id=update.message.chat_id,
                         text=tags)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Add some tags')


def add_tag(bot, update, args):
    Tag.create(user=_current_user(update.message.from_user),
               title=args[0])


def bookmark(bot, update):
    _resend_message_with_markup(bot, update)


def set_bookmark(bot, update):
    message = Message.get(Message.telegram_id == update.callback_query.message.message_id)
    message.update_tag(update.callback_query.data)

    bot.edit_message_reply_markup(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            reply_markup=_build_markup(
                _current_user(update.callback_query.from_user),
                message))

def _resend_message_with_markup(bot, update):
    # !!! Only 8 messages in a row available
    # !!! Any number of rows available(at high numbers breaks shit)
    message, _ = Message.get_or_create(text=update.message.caption,
                                       user=_current_user(update.message.from_user))
    telegram_message = bot.send_message(chat_id=update.message.chat_id,
                                        text=update.message.caption,
                                        reply_markup=_build_markup(
                                            _current_user(update.message.from_user),
                                            message))
    message.telegram_id = telegram_message.message_id
    message.save()


def _update_message_markup(bot, update):
    return None;


def _current_user(telegram_user):
    user, _ = User.get_or_create(
                id=telegram_user.id,
                defaults={'first_name': telegram_user.first_name,
                          'last_name': telegram_user.last_name,
                          'username': telegram_user.username})
    return user

def _current_message(update):
    return Message.get(Message.telegram_id == update.message.id)

def _build_markup(user, message):
    tags = user.popular_tags()
    current_tags = [tag.title for tag in message.all_tags()]
    row = []
    markup = []

    for tag in tags:
        row.append(InlineKeyboardButton(
                    ("✔ " if tag.title in current_tags else "❌ ") + tag.title,
                    callback_data=tag.id))

        if len(row) == MAX_BUTTONS_IN_ROW:
            markup.append(row)
            row = []

    if len(row):
        markup.append(row)

    return InlineKeyboardMarkup(markup)
