__all__ = [
	"AnystatError"
]

class AnystatError(Exception):
	"""Base class for errors raised by the Anystat."""
	pass

class APIError(AnystatError):
	"""Base for errors arising from an interaction with the API."""
	def __init__(self, message: str) -> None:
		super().__init__(message)
		self.message = message

class APIConnectionError(APIError):
	"""The request could not reach the API."""
	def __init__(self, message: str = "Could not connect to Anystat.") -> None:
		super().__init__(message)

class APITimeoutError(APIConnectionError):
	"""The request exceeded the timeout."""
	def __init__(self, message = "Request timed out."):
		super().__init__(message)