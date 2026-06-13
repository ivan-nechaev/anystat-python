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
		
		#CommandStart
		if event.message and event.message.text == "/start":
			pass
		
		#Message
		elif event.message:
			pass

		#Command
		elif event.message and event.message.text.startswith("/"):
			pass

		#CallbackQuery
		elif event.callback_query:
			pass

		#MyChatMember
		elif event.my_chat_member:
			pass

