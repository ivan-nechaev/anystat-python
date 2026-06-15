from __future__ import annotations

import httpx

ENV_API_KEY = "ANYSTAT_API_KEY"

DEFAULT_BASE_URL ="https://api.anystat.me"
DEFAULT_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)