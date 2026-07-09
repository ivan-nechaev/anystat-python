from __future__ import annotations

import httpx

ENV_API_KEY = "ANYSTAT_API_KEY"

DEFAULT_BASE_URL = "https://api.anystat.me"

DEFAULT_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)


MAX_EVENT_BATCH_SIZE = 30
MAX_IDENTIFY_BATCH_SIZE = 10

FLUSH_INTERVAL = 60.0

INITIAL_RETRY_DELAY = 0.5  # seconds
MAX_RETRY_DELAY = 15.0 # seconds
RETRY_STATUS_CODES = frozenset({408, 409, 429, 500, 502, 503, 504})
DEFAULT_MAX_RETRIES = 2