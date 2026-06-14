from __future__ import annotations

import os

from ._config import AnystatConfig
from .errors import AnystatError
from ._constants import ENV_API_KEY


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

		debug: bool = None,
		track_start: bool = None,
		track_callback_query: bool = None,
		track_messages: bool = None,
		auto_identify: bool = None
	) -> None:
		
		key = api_key if api_key is not None else os.environ.get(ENV_API_KEY)
		if not key:
			raise AnystatError(
				f"No API key provided. Pass api_key=..."
				f"or set the {ENV_API_KEY} envirnment variable."
			)
		
		self.api_key=key

		base_config = config or AnystatConfig()

		self.debug = debug if debug is not None else base_config.debug
		self.track_start = track_start if track_start is not None else base_config.track_start
		self.track_callback_query = track_callback_query if track_callback_query is not None else base_config.track_callback_query
		self.track_messages = track_messages if track_messages is not None else base_config.track_messages
		self.auto_identify = auto_identify if auto_identify is not None else base_config.auto_identify