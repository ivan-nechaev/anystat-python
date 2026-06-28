from __future__ import annotations
from enum import Enum
import time
from typing import Any, Literal, TypeAlias

from pydantic import Field
from ._base import AnystatModel




class EventType(str, Enum):
	MESSAGE = "message"
	CALLBACK_QUERY = "callback_query"
	MY_CHAT_MEMBER = "my_chat_member"
	COMMAND = "command"
	START_COMMAND = "start_command"
	CUSTOM = "custom"

MyChatMemberStatus = Literal[
	"creator",
	"administrator",
	"member",
	"restricted",
	"left",
	"kicked"
]

class IdentifiedUser(AnystatModel):
	user_id: int
	username: str | None = None
	first_name: str | None = None
	last_name: str | None = None
	language_code: str | None = None
	is_premium: bool = False


class BaseEvent(AnystatModel):
	"""Base fields, for all eventts in Telegram."""
	event_type: EventType
	user_id: int
	received_at: int
	duration: int #ms

class BaseMessageEvent(BaseEvent):
	"""Base Pydantic data model for Telegram events associated with a specific message context."""
	message_id: int | None = None

class MessageEvent(BaseMessageEvent):
	"""Pydantic data model for a message."""
	event_type: Literal[EventType.MESSAGE] = EventType.MESSAGE
	text: str

class CallbackQueryEvent(BaseMessageEvent):
	"""Pydantic data model for a Telegram callback query event triggered by inline keyboard button press."""
	event_type: Literal[EventType.CALLBACK_QUERY] = EventType.CALLBACK_QUERY
	data: str | None = None
	inline_message_id: str | None = None

class MyChatMemberEvent(BaseEvent):
	"""Pydantic data model for changes in the bot’s own chat member status."""
	event_type: Literal[EventType.MY_CHAT_MEMBER] = EventType.MY_CHAT_MEMBER
	old_status: MyChatMemberStatus
	new_status: MyChatMemberStatus


class CommandEvent(BaseMessageEvent):
	"""Pydantic data model for a detected bot command extracted from a Telegram message."""
	event_type: Literal[EventType.COMMAND] = EventType.COMMAND
	command: str

class StartCommandEvent(BaseMessageEvent):
	"""Pydantic data model for the /start command event received from a Telegram user."""
	event_type: Literal[EventType.START_COMMAND] = EventType.START_COMMAND
	start_param: str | None = None


class CustomEvent(AnystatModel):
	"""Pydantic data model for a custom event."""
	event_type: Literal[EventType.CUSTOM] = EventType.CUSTOM
	custom_name: str
	user_id: int | None = None
	received_at: int = Field(default_factory=lambda: int(time.time()))
	properties: dict[str, Any]



Event: TypeAlias = (
	MessageEvent
	| CallbackQueryEvent
	| MyChatMemberEvent
	| CommandEvent
	| StartCommandEvent
	| CustomEvent
)