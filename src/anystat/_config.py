from __future__ import annotations

class AnystatConfig:
	"""
	Configuration class for Anystat.

	This class is used to configure the behavior of the Anystat client.
	You can either pass parameters directly to `Anystat(...)` or create
	an instance of this class and pass it via the `config` argument.

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
		debug: bool = False,
		api_key: str | None = None,

		track_start: bool = True,
		track_callback_query: bool = True,
		track_messages: bool = False,
		auto_identify: bool = False
	) -> None:
		self.debug=debug
		self.api_key=api_key
		self.track_start=track_start
		self.track_callback_query=track_callback_query
		self.track_messages=track_messages
		self.auto_identify=auto_identify
