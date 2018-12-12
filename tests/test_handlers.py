import pytest
import telegram
from .context import handlers, models
from .factories import *
import mock

@pytest.mark.usefixtures("init_tables")
class TestCommands(object):
    @mock.patch('telegram.Bot.send_message')
    def test_start_with_no_tags(self, bot, telegram_update_command):
        handlers.start(bot, telegram_update_command)

        bot.send_message.assert_called_once_with(
                chat_id=1, text='Add some tags')

    @mock.patch('telegram.Bot.send_message')
    def test_start_three_tags(self, bot, telegram_update_command, test_user):
        user = test_user
        user.tags = TagFactory.create_batch(3, user=user)
        user.save()
        handlers.start(bot, telegram_update_command)

        bot.send_message.assert_called_once_with(
                chat_id=1, text=', '.join([tag.title for tag in user.tags]))

    @mock.patch('src.models.Tag.create')
    def test_add_tag(self, bot, telegram_update_command, test_user):
        handlers.add_tag(bot, telegram_update_command, ['test'])

        models.Tag.create.assert_called_once_with(
            user=test_user,
            title='test')

    @mock.patch('telegram.Bot.send_message')
    def test_search_messages(self, bot, telegram_update_command):
        tag = TagFactory.create()
        messages = MessageFactory.create_batch(3)
        for message in messages:
            MessageTagsFactory.create(tag=tag, message=message)

        handlers.search_messages(bot, telegram_update_command, [tag.title])
        assert bot.send_message.call_count == len(messages)

@pytest.mark.usefixtures("init_tables")
class TestInlineCallbacks(object):
    @mock.patch('telegram.Bot.edit_message_reply_markup')
    def test_update_message_tags(self, bot, telegram_update_callback_tag, mocker):
        message = MessageFactory.create(telegram_id=1)
        tag = TagFactory.create()
        mocker.patch.object(models.User, 'popular_tags', return_value=[tag])
        handlers.update_message_tags(bot, telegram_update_callback_tag)

        bot.edit_message_reply_markup.assert_called_once()
        models.User.popular_tags.assert_called_once_with(1)

    @mock.patch('telegram.Bot.edit_message_reply_markup')
    def test_set_bookmark(self, bot, telegram_update_callback_tag):
        message = MessageFactory.create(telegram_id=1)
        tag = TagFactory.create()
        handlers.set_bookmark(bot, telegram_update_callback_tag)

        bot.edit_message_reply_markup.assert_called_once()
        assert models.Message.get_by_tags([tag]).count() == 1

        handlers.set_bookmark(bot, telegram_update_callback_tag)
        assert models.Message.get_by_tags([tag]).count() == 0

    @mock.patch('telegram.Bot.delete_message')
    def test_clear_message_from_history(self, bot, telegram_update_callback_done):
        message = MessageFactory.create(telegram_id=1)
        handlers.clear_message_from_history(bot, telegram_update_callback_done)

        bot.delete_message.assert_called_once_with(chat_id=1, message_id=1)

@pytest.mark.usefixtures("init_tables")
class TestForwardMessages(object):
    @mock.patch('telegram.Bot.send_message')
    def test_bookmark(self, bot, telegram_update_message_forward, test_user, mocker):
        handlers.bookmark(bot, telegram_update_message_forward)

        bot.send_message.assert_called_once()
        assert models.Message.select().count() == 1
        assert models.Message.select().first().telegram_id == 1
