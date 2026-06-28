import random

from anystat._constants import INITIAL_RETRY_DELAY, MAX_RETRY_DELAY, RETRY_STATUS_CODES


def is_retry_status_code(status_code: int) -> bool:
	return status_code in RETRY_STATUS_CODES

def retry_delay(attempt: int) -> float:
	"""Second to sleep before retry."""
	base = min(INITIAL_RETRY_DELAY * (2 ** attempt), MAX_RETRY_DELAY)
	return base * (1 - 0.25 * random.random())