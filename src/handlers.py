from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from src.models import User, Tag, Message
import json

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

def search_messages(bot, update, args):
    tags = Tag.select(Tag).where(Tag.title.in_(args))
    messages = Message.get_by_tags(tags)

    for message in messages:
        bot.send_message(chat_id=update.message.chat_id,
                         text=message.text,
                         reply_markup=_build_markup(
                             _current_user(update.message.from_user),
                             message))


def update_message_tags(bot, update):
    callback_data = _parse_callback_data(update.callback_query.data)
    message = Message.get(Message.telegram_id == update.callback_query.message.message_id)
    _edit_message_markup(bot, update, message)


def bookmark(bot, update):
    _resend_message_with_markup(bot, update)


def set_bookmark(bot, update):
    callback_data = _parse_callback_data(update.callback_query.data)
    message = Message.get(Message.telegram_id == update.callback_query.message.message_id)
    message.update_tag(callback_data['tag_id'])
    _edit_message_markup(bot, update, message)

def clear_message_from_history(bot, update):
    callback_data = _parse_callback_data(update.callback_query.data)
    if callback_data['done']:
        bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)

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


def _edit_message_markup(bot, update, message):
    bot.edit_message_reply_markup(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            reply_markup=_build_markup(
                _current_user(update.callback_query.from_user),
                message,
                _current_page(update)))

def _current_user(telegram_user):
    user, _ = User.get_or_create(
                id=telegram_user.id,
                defaults={'first_name': telegram_user.first_name,
                          'last_name': telegram_user.last_name,
                          'username': telegram_user.username})
    return user

def _current_message(update):
    return Message.get(Message.telegram_id == update.message.id)

def _current_page(update):
    callback_data = _parse_callback_data(update.callback_query.data)
    if callback_data['page'] and callback_data['page'] > 0:
        return callback_data['page']
    else:
        return 1

def _build_markup(user, message, page=1):
    max_page = user.max_tag_page()
    if max_page < page:
        page = max_page
    tags = user.popular_tags(page)
    current_tags = [tag.title for tag in message.all_tags()]
    row = []
    markup = []

    for tag in tags:
        row.append(InlineKeyboardButton(
                    ("✅ " if tag.title in current_tags else "❌ ") + tag.title,
                    callback_data=_build_tag_callback_data(tag, page)))

        if len(row) == MAX_BUTTONS_IN_ROW:
            markup.append(row)
            row = []

    if len(row):
        markup.append(row)

    footer = []
    if page != 1:
        footer.append(InlineKeyboardButton('<', callback_data=json.dumps({'page': page - 1})))
    footer.append(InlineKeyboardButton('Done', callback_data=_build_done_callback_data()))
    if page != max_page:
        footer.append(InlineKeyboardButton('>', callback_data=json.dumps({'page': page + 1})))

    markup.append(footer)
    return InlineKeyboardMarkup(markup)

def _build_tag_callback_data(tag, current_page):
    return json.dumps({'tag_id': tag.id, 'page': current_page})

def _build_done_callback_data():
    return json.dumps({'done': True})

def _parse_callback_data(data):
    return json.loads(data)
