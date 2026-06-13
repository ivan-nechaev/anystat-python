from __future__ import annotations

import os

from .errors import AnystatError
from ._constants import ENV_API_KEY


class Anystat:
	"""Anystat client.
	
	>>> from anystat import Anystat, setup_anystat
	>>> anystat = Anystat(...)
	>>> setup_anystat(anystat, dp)
	"""

	def __init__(
		self,
		*,
		api_key: str | None = None,
		debug: bool = False,
	) -> None:
		key = api_key if api_key is not None else os.environ.get(ENV_API_KEY)
		if not key:
			raise AnystatError(
				f"No API key provided. Pass api_key=..."
				f"or set the {ENV_API_KEY} envirnment variable."
			)
		
		self.api_key: str = key
		self.debug = debug