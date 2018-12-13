from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from enum import Enum
from src.models import (
    User, Tag, Message, ReplyMarkupMessage, current_user
)
from src.reply_keyboards import pagination_keyboard
import json
import re

MAX_BUTTONS_IN_ROW = 2
TAGS_PER_PAGE = 3
FORWARDED_MESSAGES_PER_PAGE = 3
SENDED_MESSAGES_PER_PAGE = 3

class TelegramHandler:
    def __init__(self, bot, update):
        self.bot = bot
        self.update = update

    def _correct_page(self, page, max_page):
        if page < 1:
            return 1
        elif page > max_page:
            return max_page
        else:
            return page

    def _max_page(self, query, per_page):
        count = query.count()
        if count < per_page:
            return 1
        elif count % per_page == 0:
            return count/per_page
        else:
            return round(count/per_page) + 1

    def _send_messages(self, messages):
        for message in messages:
            self.bot.send_message(chat_id=self.update.message.chat_id,
                                  text=message.text,
                                  reply_markup=self._build_markup(message))

    def _send_reply_markup(self, text, reply_markup, params):
        chat_id = self.update.message.chat_id
        previous_message = self.user.reply_markup_message
        if previous_message.exists():
            self.bot.delete_message(chat_id=chat_id,
                                    message_id=previous_message.get().telegram_id)
        message = self.bot.send_message(
                         chat_id=chat_id,
                         text=text,
                         reply_markup=reply_markup)
        ReplyMarkupMessage.create(
            telegram_id=message.message_id,
            params=params,
            user=self.user)

    def _build_markup(self, message, page=1):
        max_page = self._max_page(self.user.tags, TAGS_PER_PAGE)
        page = self._correct_page(page, max_page)
        current_tags = [tag.title for tag in message.all_tags()]
        tags = self.user.popular_tags(page, TAGS_PER_PAGE)
        row = []
        markup = []

        for tag in tags:
            row.append(InlineKeyboardButton(
                        ("✅ " if tag.title in current_tags else "❌ ") + tag.title,
                        callback_data=self._build_tag_callback_data(tag, page)))

            if len(row) == MAX_BUTTONS_IN_ROW:
                markup.append(row)
                row = []

        if len(row):
            markup.append(row)

        footer = []
        if page != 1:
            footer.append(InlineKeyboardButton(
                '<', callback_data=json.dumps({'page': page - 1})))
        footer.append(InlineKeyboardButton(
            'Done', callback_data=self._build_done_callback_data()))
        if page != max_page:
            footer.append(InlineKeyboardButton(
                '>', callback_data=json.dumps({'page': page + 1})))

        markup.append(footer)
        return InlineKeyboardMarkup(markup)

    def _build_tag_callback_data(self, tag, current_page):
        return json.dumps({'tag_id': tag.id, 'page': current_page})

    def _build_done_callback_data(self):
        return json.dumps({'done': True})

class CommandHandler(TelegramHandler):
    def __init__(self, bot, update, args=None):
        super().__init__(bot, update)
        self.user = current_user(update.message.from_user)
        if args:
            self.args = args
        self._call_handler()

    def start(self):
        tags = [tag.title for tag in self.user.tags]
        if tags:
            self.bot.send_message(chat_id=self.update.message.chat_id,
                                  text=', '.join(tags))
        else:
            self.bot.send_message(chat_id=self.update.message.chat_id,
                                  text='Add some tags')

    def add_tag(self):
        Tag.create(user=self.user, title=self.args[0])

    def search_messages(self):
        tags = (Tag.select(Tag)
                  .where(Tag.user == self.user)
                  .where(Tag.title.in_(self.args)))
        messages = Message.get_by_tags(tags)
        messages = messages.paginate(1, paginate_by=SENDED_MESSAGES_PER_PAGE)

        self._send_reply_markup(
            'Messages: ',
            pagination_keyboard(),
            json.dumps(
                ReplyMarkupMessage.search_params(self.args)))
        self._send_messages(messages)

    def _call_handler(self):
        {
            '/start': self.start,
            '/tag': self.add_tag,
            '/search': self.search_messages
        }[self._command()]()

    def _command(self):
        from_index = self.update.message.entities[0].offset
        to_index = from_index + self.update.message.entities[0].length
        return self.update.message.text[from_index:to_index]


class ForwardMessageHandler(TelegramHandler):
    def __init__(self, bot, update, args=None):
        super().__init__(bot, update)
        self.user = current_user(update.message.from_user)
        self._resend_message_with_markup()

    def _resend_message_with_markup(self):
        # !!! Only 8 messages in a row available
        # !!! Any number of rows available(at high numbers breaks shit)
        message_text = self._get_message_text()
        message, _ = Message.get_or_create(
                text=message_text,
                user=self.user)

        telegram_message = self.bot.send_message(
                chat_id=self.update.message.chat_id,
                text=message_text,
                reply_markup=self._build_markup(message))
        message.telegram_id = telegram_message.message_id
        message.save()

    def _get_message_text(self):
        if self.update.message.text:
            return self.update.message.text
        else:
            return self.update.message.caption

class InlineCallbackHandler(TelegramHandler):
    class Action(Enum):
        SET_TAG = "^.*?\\btag_id\\b.*?$"
        DONE = "^.*?\\bdone\\b.*?$"
        PAGINATE="^.*?\\bpage\\b.*?$"

        @classmethod
        def match(cls, callback_data):
            for action in cls:
                if re.match(action.value, callback_data):
                    return action

    def __init__(self, bot, update, args=None):
        super().__init__(bot, update)
        self.user = current_user(update.callback_query.from_user)
        self.message = Message.get(
            Message.telegram_id == update.callback_query.message.message_id)
        self.callback_data = json.loads(update.callback_query.data)
        self._call_handler()

    def update_message_tags(self):
        self._edit_message_markup()

    def set_tag(self):
        self.message.update_tag(self.callback_data['tag_id'])
        self._edit_message_markup()

    def clear_message_from_history(self):
        self.bot.delete_message(
            chat_id=self.update.callback_query.message.chat_id,
            message_id=self.update.callback_query.message.message_id)

    def current_page(self):
        if self.callback_data['page'] and self.callback_data['page'] > 0:
            return self.callback_data['page']
        else:
            return 1

    def _edit_message_markup(self):
        self.bot.edit_message_reply_markup(
                chat_id=self.update.callback_query.message.chat_id,
                message_id=self.update.callback_query.message.message_id,
                reply_markup=self._build_markup(
                    self.message,
                    self.current_page()))

    def _build_tag_callback_data(self, tag, current_page):
        return json.dumps({'tag_id': tag.id, 'page': current_page})

    def _build_done_callback_data(self):
        return json.dumps({'done': True})

    def _call_handler(self):
        {
            self.Action.SET_TAG: self.set_tag,
            self.Action.DONE: self.clear_message_from_history,
            self.Action.PAGINATE: self.update_message_tags
        }[self.Action.match(self.update.callback_query.data)]()


class ReplyKeyboardCallbackHandler(TelegramHandler):
    def __init__(self, bot, update, args=None):
        super().__init__(bot, update)
        self.user = current_user(update.message.from_user)
        self.current_params = self.user.reply_markup_message.get().decoded_params()
        self.get_messages()

    def get_messages(self):
        tags = (Tag.select(Tag)
                  .where(Tag.user == self.user)
                  .where(Tag.title.in_(self.current_params['tags'])))
        messages = Message.get_by_tags(tags)

        if self.update.message.text == '<':
            page = self.current_params['page'] - 1
        elif self.update.message.text == '>':
            page = self.current_params['page'] + 1
        page = self._correct_page(
                page,
                self._max_page(messages, SENDED_MESSAGES_PER_PAGE))
        messages = messages.paginate(page, paginate_by=SENDED_MESSAGES_PER_PAGE)

        self._send_reply_markup(
                'Messages: ',
                pagination_keyboard(),
                json.dumps(ReplyMarkupMessage.search_params(self.current_params['tags'], page)))
        self._send_messages(messages)
