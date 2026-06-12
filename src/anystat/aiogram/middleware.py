from __future__ import annotations
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import Update
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