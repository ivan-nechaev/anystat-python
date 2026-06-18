from unittest.mock import MagicMock

from anystat._models.models import (
	CallbackQueryEvent,
	CommandEvent,
	MessageEvent,
	MyChatMemberEvent,
	StartCommandEvent
)

from anystat.aiogram.middleware import AnystatMiddleware
import pytest


@pytest.fixture
def anystat():
	mock = MagicMock()
	mock.track_start = True
	mock.track_messages = True
	mock.auto_identify = True
	return mock

@pytest.fixture
def middleware(anystat):
	return AnystatMiddleware(anystat)

@pytest.mark.parametrize("auto_identify", [False, True])
def test_identify_user(middleware, auto_identify):
	"""Проверка авто индетификации пользователя."""
	middleware.anystat.auto_identify = auto_identify

	mock_user = MagicMock()
	mock_user.id = 52
	mock_user.username = "test_username"
	mock_user.first_name = "test_first_name"
	mock_user.last_name = None
	mock_user.language_code = "en"
	mock_user.is_premium = False

	data = {"event_from_user": mock_user}
	result = middleware._identify(data)

	if auto_identify:
		assert result.user_id == 52
		assert result.username == "test_username"
	else:
		assert result is None


@pytest.mark.parametrize("track_messages", [False, True])
def test_get_regular_message(middleware, track_messages):
	"""Проверка определения события обычного сообщения."""
	middleware.anystat.track_messages = track_messages

	mock_message = MagicMock()
	mock_message.text = "test"
	mock_message.from_user.id = 52
	mock_message.message_id = 123

	result = middleware._get_message_event(mock_message, received_at=10, duration=230)

	if track_messages:
		assert isinstance(result, MessageEvent)
		assert result.user_id == 52
		assert result.duration == 230
	else:
		assert result is None

@pytest.mark.parametrize("track_start", [False, True])
def test_get_command_start(middleware, track_start):
	"""Проверка определения события /start."""
	middleware.anystat.track_start = track_start

	mock_message = MagicMock()
	mock_message.text = "/start ref"
	mock_message.from_user.id = 52
	mock_message.message_id = 123

	result = middleware._get_message_event(mock_message, received_at=10, duration=230)

	if track_start:
		assert isinstance(result, StartCommandEvent)
		assert result.user_id == 52
		assert result.duration == 230
		assert result.start_param == "ref"
	else:
		assert result is None

@pytest.mark.parametrize("track_command", [False, True])
def test_get_command(middleware, track_command):
	"""Проверка определения события команды."""
	middleware.anystat.track_command = track_command

	mock_message = MagicMock()
	mock_message.text = "/command"
	mock_message.from_user.id = 52
	mock_message.message_id = 123
	
	result = middleware._get_message_event(mock_message, received_at=10, duration=230)

	if track_command:
		assert isinstance(result, CommandEvent)
		assert result.user_id == 52
		assert result.duration == 230
		assert result.command == "/command"
	else: 
		assert result is None

def test_get_callback_query(middleware):
	"""Проверка определения события callback."""
	mock_callback = MagicMock()
	mock_callback.from_user.id = 52
	mock_callback.message.message_id = 123
	mock_callback.data = "action"
	mock_callback.inline_message_id = "123"

	result = middleware._get_callback_query_event(mock_callback, received_at=10, duration=230)

	assert isinstance(result, CallbackQueryEvent)
	assert result.user_id == 52
	assert result.duration == 230
	assert result.inline_message_id == "123"
	assert mock_callback.data == "action"

def test_get_my_chat_member(middleware):
	mock_member = MagicMock()
	mock_member.from_user.id = 52
	mock_member.old_chat_member.status = 'member'
	mock_member.new_chat_member.status = 'kicked'

	result = middleware._get_my_chat_member_event(mock_member, received_at=10, duration=230)
	
	assert isinstance(result, MyChatMemberEvent)
	assert result.old_status == 'member'
	assert result.new_status == 'kicked'