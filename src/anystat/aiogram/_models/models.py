from __future__ import annotations
from enum import Enum
from typing import Literal, Optional
from ._base import AnystatModel


class EventType(str, Enum):
	MESSAGE = "message"
	CALLBACK_QUERY = "callback_query"
	MY_CHAT_MEMBER = "my_chat_member"
	COMMAND = "command"
	START_COMMAND = "start_command"

MyChatMemberStatus = Literal[
	"creator",
	"administrator",
	"member",
	"restricted",
	"left",
	"kicked"
]

class BaseEvent(AnystatModel):
	"""Base fields, for all eventts in Telegram."""
	eventType: EventType
	user_id: int
	timestamp: int


class CallbackQueryEvent(BaseEvent):
	"""Pydantic data model for a Telegram callback query event triggered by inline keyboard button press."""
	eventType: Literal[EventType.CALLBACK_QUERY]
	data: Optional[str] = None
	message_id: Optional[int] = None
	inline_message_id: Optional[str] = None

class MyChatMemberEvent(BaseEvent):
	"""Pydantic data model for changes in the bot’s own chat member status."""
	event_type: Literal[EventType.MY_CHAT_MEMBER]
	old_status: MyChatMemberStatus
	new_status: MyChatMemberStatus


class CommandEvent(BaseEvent):
	"""Pydantic data model for a detected bot command extracted from a Telegram message."""
	event_type: Literal[EventType.COMMAND]
	command: str
	message_id: int

class StartCommandEvent(BaseEvent):
	"""Pydantic data model for the /start command event received from a Telegram user."""
	event_type: Literal[EventType.START_COMMAND]
	start_param: Optional[str] = None
	message_id: int