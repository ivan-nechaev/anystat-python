from __future__ import annotations

import os
from typing import TypeVar
import httpx

from ._batcher import AnystatBatcher
from ._models.models import CustomEvent, Event

from ._config import AnystatConfig
from .errors import AnystatError
from ._constants import DEFAULT_TIMEOUT, ENV_API_KEY, FLUSH_INTERVAL, MAX_EVENT_BATCH_SIZE, MAX_IDENTIFY_BATCH_SIZE

T = TypeVar("T")

class Anystat:
	"""
	Main client for Anystat — analytics for Telegram bots.

	It supports both simple configuration via parameters and more advanced
	configuration via the `AnystatConfig` class.

	You can either pass parameters directly to the constructor or create
	a config object and pass it via the `config` argument.

	Example:
			>>> from anystat import Anystat, setup_anystat
			>>> anystat = Anystat(api_key=..., debug=True)
			>>> setup_anystat(dp, anystat)

	Attributes:
			debug (bool):
					If True, enables debug mode. In this mode, Anystat will print
					to the console every event being tracked and the exact data
					that is being sent to the server. Useful for development and
					for understanding what information is collected.

			api_key (str | None):
					Your Anystat API key. Can also be passed directly to `Anystat(...)`
					or set via the `ANYSTAT_API_KEY` environment variable.

			track_start (bool):
					Whether to automatically track the `/start` command.
					Enabled by default.

			track_command (bool):
					Whether to automatically track commands.
					Enabled by default.

			track_callback_query (bool):
					Whether to automatically track clicks on inline keyboard buttons
					(callback queries). Enabled by default.

			track_messages (bool):
					Whether to automatically track all incoming text messages.
					Disabled by default for privacy reasons.

			auto_identify (bool):
					Whether to automatically call `identify()` when a user first
					interacts with the bot. Disabled by default for privacy reasons. 
	"""

	def __init__(
		self,
		*,
		api_key: str | None = None,
		config: AnystatConfig | None = None,

		debug: bool | None = None,
		track_start: bool | None = None,
		track_callback_query: bool | None = None,
		track_messages: bool | None = None,
		track_command: bool | None = None,
		auto_identify: bool | None = None,

	) -> None:
		
		key = api_key if api_key is not None else os.environ.get(ENV_API_KEY)
		if not key:
			raise AnystatError(
				f"No API key provided. Pass api_key=..."
				f"or set the {ENV_API_KEY} envirnment variable."
			)
		
		self.api_key = key
		self._http = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)

		base_config = config or AnystatConfig()

		self._event_batcher = AnystatBatcher[Event](
			max_batch_size=MAX_EVENT_BATCH_SIZE,
			flush_interval=FLUSH_INTERVAL,
		)
		self._identify_batcher = AnystatBatcher[Event](
			max_batch_size=MAX_IDENTIFY_BATCH_SIZE,
			flush_interval=FLUSH_INTERVAL,
		)

		self.debug = debug if debug is not None else base_config.debug
		self.track_start = track_start if track_start is not None else base_config.track_start
		self.track_command = track_command if track_command is not None else base_config.track_command
		self.track_callback_query = track_callback_query if track_callback_query is not None else base_config.track_callback_query
		self.track_messages = track_messages if track_messages is not None else base_config.track_messages
		self.auto_identify = auto_identify if auto_identify is not None else base_config.auto_identify


	def track(self, name: str, user_id: int | None, **kwargs):
		return CustomEvent(
			name=name,
			user_id=user_id,
			properties=kwargs
		)
	

	async def close(self) -> None:
		await self._event_batcher.kill()
		await self._identify_batcher.kill()
		await self._http.aclose()