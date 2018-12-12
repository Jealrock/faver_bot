import pytest
import json
from .factories import UserFactory, drop_tables, create_tables
from telegram import Update


@pytest.fixture
def init_tables(request):
    create_tables()

    def finalize():
        drop_tables()

    request.addfinalizer(finalize)


@pytest.fixture
def bot(mocker):
    with mocker.patch('telegram.Bot') as MockBot:
        return MockBot()


@pytest.fixture
def telegram_update_command(mocker):
    with open('tests/data/telegram_update_command.json') as f:
        with mocker.patch('telegram.Bot') as MockBot:
            return Update.de_json(json.load(f), MockBot)


@pytest.fixture
def telegram_update_callback_tag(mocker):
    with open('tests/data/telegram_update_callback_tag.json') as f:
        with mocker.patch('telegram.Bot') as MockBot:
            return Update.de_json(json.load(f), MockBot)


@pytest.fixture
def telegram_update_callback_done(mocker):
    with open('tests/data/telegram_update_callback_done.json') as f:
        with mocker.patch('telegram.Bot') as MockBot:
            return Update.de_json(json.load(f), MockBot)


@pytest.fixture
def telegram_update_message_forward(mocker):
    with open('tests/data/telegram_update_message_forward.json') as f:
        with mocker.patch('telegram.Bot') as MockBot:
            return Update.de_json(json.load(f), MockBot)


@pytest.fixture
def test_user():
    return UserFactory.create(
            id=1,
            defaults={'first_name': 'test_first_name',
                      'last_name': 'test_last_name',
                      'username': 'test_username'})
