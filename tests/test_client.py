from __future__ import annotations

import pytest
from anystat import AnystatError, Anystat, AnystatConfig


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
		auto_identify=True,
		track_messages=True
	)
	anystat = Anystat(api_key="API_KEY", config=config)

	assert anystat.debug == True
	assert anystat.track_messages == True
	assert anystat.auto_identify == True