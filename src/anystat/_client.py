from __future__ import annotations

import asyncio
import logging
import os
from typing import List, TypeVar
import warnings
import httpx

from ._batcher import AnystatBatcher
from ._models.models import CustomEvent, Event
from ._retry import retry_delay, is_retry_status_code
from ._config import AnystatConfig
from .errors import APIConnectionError, APITimeoutError, AnystatError
from ._constants import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, ENV_API_KEY, FLUSH_INTERVAL, MAX_EVENT_BATCH_SIZE, MAX_IDENTIFY_BATCH_SIZE

T = TypeVar("T")

logger = logging.getLogger("anystat")
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
		self.max_retries: int = DEFAULT_MAX_RETRIES

		base_config = config or AnystatConfig()

		self._event_batcher = AnystatBatcher[Event](
			max_batch_size=MAX_EVENT_BATCH_SIZE,
			flush_interval=FLUSH_INTERVAL,
			flush_callback=self._send_events
		)
		self._identify_batcher = AnystatBatcher[Event](
			max_batch_size=MAX_IDENTIFY_BATCH_SIZE,
			flush_interval=FLUSH_INTERVAL,
			flush_callback=self._send_events
		)

		self.debug = debug if debug is not None else base_config.debug
		self.track_start = track_start if track_start is not None else base_config.track_start
		self.track_command = track_command if track_command is not None else base_config.track_command
		self.track_callback_query = track_callback_query if track_callback_query is not None else base_config.track_callback_query
		self.track_messages = track_messages if track_messages is not None else base_config.track_messages

		if auto_identify or base_config.auto_identify:
			logger.warning(
				"Auto_identify is not available in this version. User profile "
				"collection is under legal review and will be enabled in a "
				"future release. No data was sent.",
				stacklevel=2,
			)
		self.auto_identify = False



	async def _request(self, method: str, path: str, json: dict) -> httpx.Response:
		url = f"{DEFAULT_BASE_URL}{path}"

		for attempt in range(self.max_retries + 1):
			try:
				response = await self._http.request(
					method, url,
					json=json,
					headers={"X-API-Key": self.api_key}
				)
			except httpx.TimeoutException as e:
				if attempt < self.max_retries:
					await asyncio.sleep(retry_delay)
					continue
				raise APITimeoutError() from e
			except httpx.HTTPError as e:
				if attempt < self.max_retries:
					await asyncio.sleep(retry_delay)
					continue
				raise APIConnectionError(str(e)) from e
			if is_retry_status_code(response.status_code) and attempt < self.max_retries:
				await asyncio.sleep(retry_delay(attempt))
				continue
			response.raise_for_status()
			return response
		raise APIConnectionError("Exhausted retries without a response.")

	async def _send_events(self, events: List[Event]) -> None:
		payload = [e.model_dump() for e in events]
		try:
			await self._request("POST", "/v1/collect/events", json=payload)
		except (APITimeoutError, APIConnectionError, httpx.HTTPError) as e:
			logger.warning("Failed to send events to Anystat (%d events): %s", len(events), e)
		except Exception:
			logger.exception("Unexpected error while sending to Anystat")

	async def track(self, name: str, user_id: int | None, **kwargs):
		event = CustomEvent(
			custom_name=name,
			user_id=user_id,
			properties=kwargs
		)
		await self._event_batcher.add(event)
	

	async def close(self) -> None:
		await self._event_batcher.kill()
		await self._identify_batcher.kill()
		await self._http.aclose()