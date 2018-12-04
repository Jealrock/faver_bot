from peewee import (
    CharField, BigIntegerField, Model, ForeignKeyField,
    fn, JOIN
)
from database import db

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = BigIntegerField(primary_key=True, index=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)

    def popular_tags(self):
        return popular_tags(self)


class Message(BaseModel):
    text = CharField()
    telegram_id = BigIntegerField(index=True, null=True)
    user = ForeignKeyField(User, backref='messages')

    def all_tags(self):
        return message_tags(self)

    def update_tag(self, tag_id):
        return update_message_tag(self, tag_id)

class Tag(BaseModel):
    title = CharField()
    user = ForeignKeyField(User, backref='tags')

class MessageTags(BaseModel):
    message = ForeignKeyField(Message)
    tag = ForeignKeyField(Tag)


def popular_tags(user, amount=3):
    count = fn.COUNT(MessageTags.id)
    return (Tag
            .select(Tag, count.alias('entry_count'))
            .join(MessageTags, JOIN.LEFT_OUTER)
            .join(Message, JOIN.LEFT_OUTER)
            .where(Tag.user == user)
            .group_by(Tag)
            .order_by(count.desc(), Tag.title)[:amount])

def message_tags(message):
    return (Tag
            .select(Tag)
            .join(MessageTags, JOIN.LEFT_OUTER)
            .where(MessageTags.message == message))

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
