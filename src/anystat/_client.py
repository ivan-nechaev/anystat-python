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
			api_key (str):
					Your Anystat API key. 
	"""

	def __init__(
		self,
		*,
		api_key: str | None = None,
		config: AnystatConfig | None = None,
		debug: bool = False
	) -> None:
		key = api_key if api_key is not None else os.environ.get(ENV_API_KEY)
		if not key:
			raise AnystatError(
				f"No API key provided. Pass api_key=..."
				f"or set the {ENV_API_KEY} envirnment variable."
			)
		
		self.api_key: str = key
		self.debug = debug