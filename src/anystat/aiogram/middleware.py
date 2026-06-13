from __future__ import annotations
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import Update
from ._models.models import BaseEvent
from .._client import Anystat

dp = Dispatcher()

class AnystatMiddleware(BaseMiddleware):
	"""Middleware for auto collecting events in Anystat."""
	def __init__(self, anystat: Anystat) -> None:
		self.anystat = anystat
	
	async def __call__(
			self,
			handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
			event: Update,
			data: dict[str, Any]
	) -> Any:
		print(event, data)

		return await handler(event, data)
	
	

	def _get_event_model(self, event: Update) -> BaseEvent | None:
		"""Selects the matching event model for the Update."""


		if event.message:
			msg = event.message
			text = msg.text or ""

			#CommandStart
			if text.startswith("/start"):
				if self.anystat.track_start:
					pass
				return None
			
			#Command
			elif text.startswith("/"):
				pass
			
			#Message
			elif event.message:
				if self.anystat.track_messages:
					pass
				return None
				
		#CallbackQuery
		elif event.callback_query:
			if self.anystat.track_callback_query:
				pass
			return None
		

		#MyChatMember
		elif event.my_chat_member:
			pass

		#Не одно не подошло
		return None