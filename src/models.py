from peewee import (
    CharField, BigIntegerField, Model, ForeignKeyField,
    fn, JOIN
)
from database import db

class BaseModel(Model):
    class Meta:
        database = db

class User(Model):
    id = BigIntegerField(primary_key=True, index=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)

    def popular_tags(self, page=1, amount=3):
        return popular_tags(self, page=page)

    def max_tag_page(self):
        return tags_max_page(self)

class Message(Model):
    text = CharField()
    telegram_id = BigIntegerField(index=True, null=True)
    user = ForeignKeyField(User, backref='messages')

    def all_tags(self):
        return message_tags(self)

    def update_tag(self, tag_id):
        return update_message_tag(self, tag_id)

    def get_by_tags(tags):
        return messages_by_tags(tags)

class Tag(Model):
    title = CharField()
    user = ForeignKeyField(User, backref='tags')

class MessageTags(Model):
    message = ForeignKeyField(Message)
    tag = ForeignKeyField(Tag)


def popular_tags(user, amount=3, page=1):
    count = fn.COUNT(MessageTags.id)
    return (Tag
            .select(Tag, count.alias('entry_count'))
            .join(MessageTags, JOIN.LEFT_OUTER)
            .join(Message, JOIN.LEFT_OUTER)
            .where(Tag.user == user)
            .group_by(Tag)
            .order_by(fn.COUNT(MessageTags.id).desc(), Tag.title)
            .paginate(page, paginate_by=amount))

def tags_max_page(user):
    tags_count = user.tags.count()
    if tags_count % 3 == 0:
        return tags_count/3
    else:
        return round(tags_count/3) + 1

def message_tags(message):
    return (Tag
            .select(Tag)
            .join(MessageTags, JOIN.LEFT_OUTER)
            .where(MessageTags.message == message))

def messages_by_tags(tags):
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
