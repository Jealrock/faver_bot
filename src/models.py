from peewee import (
    CharField, BigIntegerField, fn, Model,
    ForeignKeyField
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

    def popular_tags(amount=3):
        count = fn.COUNT(MessageTags.id)
        print((Tag
               .select(Tag, count.alias('entry_count'))
               .join(MessageTags)
               .join(Message)
               .group_by(Tag)
               .order_by(count.desc(), Tag.title)[:amount])[0])
        return []

class Message(BaseModel):
    text = CharField()
    user = ForeignKeyField(User, backref='messages')

class Tag(BaseModel):
    title = CharField()
    user = ForeignKeyField(User, backref='tags')

class MessageTags(BaseModel):
    message = ForeignKeyField(Message)
    tag = ForeignKeyField(Tag)
