from peewee import (
    CharField, BigIntegerField, Model,
    ForeignKeyField, TextField, DateTimeField,
    fn, JOIN
)
import json
from datetime import datetime, timedelta


class User(Model):
    id = BigIntegerField(primary_key=True, index=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)

    def popular_tags(self, page=1, per_page=3):
        return popular_tags(self, page=page, per_page=per_page)

    def untagged_messages(self):
        return get_untagged_messages(self)


class Message(Model):
    text = TextField()
    telegram_id = BigIntegerField(index=True, null=True)
    user = ForeignKeyField(User, backref='messages')

    def all_tags(self):
        return message_tags(self)

    def update_tag(self, tag_id):
        return update_message_tag(self, tag_id)

    def get_by_tags(tags, page=1):
        return messages_by_tags(tags, page)


class ReplyMarkupMessage(Model):
    telegram_id = BigIntegerField(index=True)
    params = CharField()
    user = ForeignKeyField(User, backref='reply_markup_message')
    created_at = DateTimeField(default=datetime.now)

    def is_recent(self):
        if self.created_at < (datetime.now() - timedelta(minutes=1)):
            return False
        else:
            return True

    def decoded_params(self):
        return json.loads(self.params)

    def search_params(tags, page=1):
        return {'action': 'search', 'page': page, 'tags': tags}

    def forward_params(page=1):
        return {'action': 'forward', 'page': page}


class Tag(Model):
    title = CharField()
    user = ForeignKeyField(User, backref='tags')


class MessageTags(Model):
    message = ForeignKeyField(Message)
    tag = ForeignKeyField(Tag)


def popular_tags(user, page=3, per_page=1):
    count = fn.COUNT(MessageTags.id)
    return (Tag
            .select(Tag, count.alias('entry_count'))
            .join(MessageTags, JOIN.LEFT_OUTER)
            .join(Message, JOIN.LEFT_OUTER)
            .where(Tag.user == user)
            .group_by(Tag)
            .order_by(fn.COUNT(MessageTags.id).desc(), Tag.title)
            .paginate(page, paginate_by=per_page))


def message_tags(message):
    return (Tag
            .select(Tag)
            .join(MessageTags, JOIN.LEFT_OUTER)
            .where(MessageTags.message == message))


def get_untagged_messages(user):
    return (Message
            .select(Message)
            .where(user == user)
            .where(Message.id.not_in(
                MessageTags.select(MessageTags.message_id)
            )))


def messages_by_tags(tags, page):
    messages = (Message
                .select(Message)
                .where(Message.id << (
                    MessageTags
                    .select(MessageTags.message_id)
                    .where(MessageTags.tag_id << [tag.id for tag in tags])
                    .group_by(MessageTags.message_id)
                    .having(fn.count(MessageTags.tag_id) == len(tags)))))
    return messages


def update_message_tag(message, tag_id):
    message_tag = (MessageTags
                   .select(MessageTags)
                   .join(Tag, JOIN.LEFT_OUTER)
                   .where(MessageTags.message == message)
                   .where(Tag.id == tag_id).first())
    if message_tag:
        message_tag.delete_instance()
    else:
        MessageTags.create(message=message,
                           tag=Tag.get_by_id(tag_id))


def current_user(telegram_user):
    user, _ = User.get_or_create(
                id=telegram_user.id,
                defaults={'first_name': telegram_user.first_name,
                          'last_name': telegram_user.last_name,
                          'username': telegram_user.username})
    return user
