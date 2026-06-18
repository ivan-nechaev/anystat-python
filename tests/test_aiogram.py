from unittest.mock import MagicMock

from aiogram import Dispatcher

from anystat.aiogram.middleware import AnystatMiddleware
from anystat.aiogram.setup import setup_anystat


def test_setup():
	dp = Dispatcher()
	anystat = MagicMock()
	
	setup_anystat(dp, anystat)

	assert any(isinstance(mw, AnystatMiddleware) for mw in dp.update.middleware._middlewares)