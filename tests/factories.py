import factory
import itertools
from factory_peewee import PeeweeModelFactory
from peewee import SqliteDatabase
from .context import models, db_initializer, db

class UserFactory(PeeweeModelFactory):
    class Meta:
        model = models.User

    id = factory.Sequence(lambda n: n)
    username = factory.Sequence(lambda n: 'user%d' % n)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class MessageFactory(PeeweeModelFactory):
    class Meta:
        model = models.Message

    text = factory.Faker('sentence')
    telegram_id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)

class TagFactory(PeeweeModelFactory):
    class Meta:
        model = models.Tag

    title = factory.Faker('sentence', nb_words=1)
    user = factory.SubFactory(UserFactory)

class MessageTagsFactory(PeeweeModelFactory):
    class Meta:
        model = models.MessageTags

    message = factory.SubFactory(MessageFactory)
    tag = factory.SubFactory(TagFactory)

class MessageWithTagsFactory(MessageFactory):
    tags = 2

    @factory.post_generation
    def message_tags(self, create, extracted):
        if create:
            MessageTagsFactory.create_batch(self.tags, message=self)

def create_tables():
    db_initializer.create_tables(db)

def drop_tables():
    db_initializer.drop_tables(db)
