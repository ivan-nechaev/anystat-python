from __future__ import annotations

from aiogram import Dispatcher
import pytest
from anystat import AnystatError, Anystat, AnystatConfig
from anystat._models.models import CustomEvent


def test_requires_api_key(monkeypatch):
	"""Если ключа нет -> ошибка."""
	monkeypatch.delenv("ANYSTAT_API_KEY", raising=False)
	with pytest.raises(AnystatError):
		Anystat()


def test_api_key_from_env(monkeypatch):
	"""Ключ из переменной окружения."""
	monkeypatch.setenv("ANYSTAT_API_KEY", "TEST_API_KEY")
	anystat = Anystat()
	assert anystat.api_key == "TEST_API_KEY"

def test_api_key_from_init():
	"""Ключ передают при создании."""
	anystat = Anystat(api_key="TEST_API_KEY")
	assert anystat.api_key == "TEST_API_KEY"
	
def test_config():
	config = AnystatConfig(
		debug=True,
		track_messages=True
	)
	anystat = Anystat(api_key="API_KEY", config=config)

	assert anystat.debug == True
	assert anystat.track_messages == True

@pytest.mark.asyncio
async def test_custom_event():
	anystat = Anystat(api_key="TEST_API_KEY")
	await anystat.track(
		"test_event",
		user_id=52,
		price=290,
		amount=10
	)

	assert isinstance(anystat._event_batcher._buffer[-1], CustomEvent)
	assert anystat._event_batcher._buffer[-1].properties["price"] == 290

@pytest.mark.asyncio
async def test_close():
	anystat = Anystat(api_key='API_KEY')

	assert anystat._http.is_closed == False
	await anystat.close()

	assert anystat._http.is_closed == True
	assert anystat._event_batcher._running == False
	assert anystat._identify_batcher._running == False