from __future__ import annotations
import time
from typing import Any, Awaitable, Callable, NotRequired

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, ChatMemberUpdated, Message, Update
from .._models.models import CallbackQueryEvent, CommandEvent, IdentifiedUser, MessageEvent, MyChatMemberEvent, StartCommandEvent
from .._client import Anystat
from aiogram.dispatcher.middlewares.data import MiddlewareData


class AnystatMiddlewareData(MiddlewareData, total=False):
	"""Expanded MiddlewareData for AnystatMiddleware."""
	received_at: NotRequired[int]
	duration: NotRequired[float]



class AnystatMiddleware(BaseMiddleware):
	"""Middleware for auto collecting events in Anystat."""
	def __init__(self, anystat: Anystat) -> None:
		self.anystat = anystat
	
	async def __call__(
			self,
			handler: Callable[[Update, MiddlewareData], Awaitable[Any]],
			event: Update,
			data: AnystatMiddlewareData
	) -> Any:
		received_at = int(time.time())
		start = time.perf_counter()

		try:
			return await handler(event, data)
		finally:
			duration = int((time.perf_counter() - start) * 1000)  # ms
			event_model = self._get_event_model(event, received_at, duration) 

			if isinstance(event_model, StartCommandEvent):
				self._identify(data) #Auto identify user
				# print(identified_user)

			data["received_at"] = received_at
			data["duration"] = duration

			if event_model is not None:
				await self.anystat._event_batcher.add(event_model)
				self.anystat._debug(f"capture {event_model.event_type.value} via AnystatMiddleware", event_model)

	def _get_event_model(self, event: Update, received_at: int, duration: float):
		if event.message:
			return self._get_message_event(event.message, received_at, duration)
		elif event.callback_query:
			return self._get_callback_query_event(event.callback_query, received_at, duration)
		elif event.my_chat_member:
			return self._get_my_chat_member_event(event.my_chat_member, received_at, duration)
		
		return None
	
	def _get_message_event(self, message: Message, received_at: int, duration: float):
		if not message.text or not message.from_user: 
			return None
		
		text = message.text.strip()
		user_id = message.from_user.id

		# /start
		if text.startswith("/start"):
			if not self.anystat.track_start:
				self.anystat._debug(f"skip /start from user={user_id} (track_start=off)")
				return None #Start command is disabled
			parts = text.split(maxsplit=1)
			start_param = parts[1] if len(parts) > 1 else None

			return StartCommandEvent(
				user_id=user_id,
				received_at=received_at,
				duration=duration,
				message_id=message.message_id,
				start_param=start_param
			)
		
		# Another command
		elif text.startswith("/"):
			if not self.anystat.track_command:
				self.anystat._debug(f"skip command from user={user_id} (track_command=off)")
				return None #Commands are disabled

			command = text.split()[0]
			return CommandEvent(
				user_id=user_id,
				received_at=received_at,
				duration=duration,
				message_id=message.message_id,
				command=command
			)
		
		else:
			if not self.anystat.track_messages:
				self.anystat._debug(f"skip message from user={user_id} (track_messages=off, text not collected)")
				return None #Messages is disabled
			
			return MessageEvent(
				user_id=user_id,
				received_at=received_at,
				duration=duration,
				text=text,
				message_id=message.message_id
			)
		
	def _get_callback_query_event(self, callback: CallbackQuery, received_at: int, duration: float):
		if not self.anystat.track_callback_query or not callback.from_user:
			self.anystat._debug("skip callback_query (track_callback_query=off or no user)")
			return None #Callback_query is disabled
		
		return CallbackQueryEvent(
			user_id=callback.from_user.id,
			received_at=received_at,
			duration=duration,
			message_id=callback.message.message_id if callback.message else None,
			data=callback.data,
			inline_message_id=callback.inline_message_id
		)

	def _get_my_chat_member_event(self, member: ChatMemberUpdated, received_at: int, duration: float):
		if not member.from_user:
			return None
		
		return MyChatMemberEvent(
			user_id=member.from_user.id,
			received_at=received_at,
			duration=duration,
			old_status=member.old_chat_member.status,
			new_status=member.new_chat_member.status
		)
	

	def _identify(self, data: MiddlewareData) -> IdentifiedUser | None:
		if not self.anystat.auto_identify:
			return None
		
		user = data.get("event_from_user")
		if not user: 
			return None
		
		return IdentifiedUser(
			user_id=user.id,
			username=user.username,
			first_name=user.first_name,
			last_name=user.last_name,
			language_code=user.language_code,
			is_premium=user.is_premium or False #тг может вернуть None (У пользователя нет премиум)
		)