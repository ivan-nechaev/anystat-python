from aiogram import Dispatcher
from .._client import Anystat
from .middleware import AnystatMiddleware


def setup_anystat(dp: Dispatcher, anystat: Anystat) -> None:
	middleware = AnystatMiddleware(anystat)
	dp.update.middleware(middleware)