from dotenv import load_dotenv
load_dotenv(dotenv_path='./.env.local')

from src.models import User, Message, Tag, MessageTags

models = [User, Message, Tag, MessageTags]


def create_tables(db):
    bind_models_to_db(db)
    db.create_tables(models)


def drop_tables(db):
    bind_models_to_db(db)
    db.drop_tables(models)


def bind_models_to_db(db):
    for model in models:
        model.bind(db)

    db.create_tables(models)
