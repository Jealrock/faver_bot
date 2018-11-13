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
    user = ForeignKeyField(User, backref='messages')

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
