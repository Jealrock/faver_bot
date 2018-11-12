from database import db
from src.models import User, Message, Tag, MessageTags

def create_tables():
    with db:
        db.create_tables([User, Message, Tag, MessageTags])

def drop_tables():
    with db:
        db.drop_tables([User, Message, Tag, MessageTags])
