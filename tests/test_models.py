import pytest
from .factories import (
    UserFactory, MessageTagsFactory, MessageFactory, TagFactory,
    MessageWithTagsFactory,
    create_tables, drop_tables
)
from .context import db, models
from playhouse.shortcuts import model_to_dict

@pytest.mark.usefixtures("init_tables")
class TestMessage(object):
    def test_all_tags(self):
        assert MessageWithTagsFactory(tags=3).all_tags().count() == 3
        assert MessageWithTagsFactory(tags=1).all_tags().count() == 1
        assert MessageFactory().all_tags().count() == 0

    def test_update_tag(self):
        tags = TagFactory.create_batch(3)
        message = MessageFactory()

        message.update_tag(tags[0].id)
        message.update_tag(tags[1].id)
        assert models.MessageTags.select(models.MessageTags).count() == 2

        message.update_tag(tags[0].id)
        assert models.MessageTags.select(models.MessageTags).count() == 1

    def test_get_by_tags(self):
        tags = TagFactory.create_batch(3)
        messages = MessageFactory.create_batch(3)
        for message in messages:
            MessageTagsFactory.create(tag=tags[0], message=message)
        MessageTagsFactory.create(tag=tags[1], message=messages[0])

        assert models.Message.get_by_tags([tags[0]]).count() == 3
        assert models.Message.get_by_tags([tags[0], tags[1]]).count() == 1
        assert models.Message.get_by_tags([tags[0], tags[2]]).count() == 0

@pytest.mark.usefixtures("init_tables")
class TestUser(object):
    def test_popular_tags(self):
        user = UserFactory()
        tags = TagFactory.create_batch(2, user=user)
        messages = MessageFactory.create_batch(2, user=user)
        for message in messages:
            message.update_tag(tags[1])

        assert user.popular_tags(page=1, amount=1)[0] == tags[1]

    def test_max_tag_page(self):
        user = UserFactory()
        tags = TagFactory.create_batch(10, user=user)

        assert user.max_tag_page() == 4;
