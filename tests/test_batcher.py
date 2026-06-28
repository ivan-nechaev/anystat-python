import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from anystat._batcher import AnystatBatcher
from anystat._models.models import CustomEvent

@pytest.fixture
def event():
	"""Фикстура с тестовым событием."""
	return CustomEvent(
			custom_name="test",
			user_id=52,
			received_at=1,
			properties={"test": 1}
	)

@pytest_asyncio.fixture
async def batcher():
	"""Фикстура с батчером."""
	async def _flush(events: list[CustomEvent]):
		"""Пустой flush для тестов (ничего не делает)."""
		pass

	_batcher = AnystatBatcher(
		max_batch_size=10,
		flush_interval=10.0,
		flush_callback=_flush
	)
	yield _batcher
	if _batcher._worker_task: await _batcher.kill()



@pytest.mark.asyncio
@pytest.mark.parametrize("events_count, expected_len", [
    (5, 5), 
    (10, 0),
])
async def test_buffer_size_and_auto_flush(event, batcher, events_count, expected_len):
	"""Проверяет размер буфера и автоматический flush при достижении max_batch_size."""
	for _ in range(events_count):
			await batcher.add(event)

	if expected_len == 0:
		await asyncio.sleep(0) #Время на очистку

	assert len(batcher._buffer) == expected_len

@pytest.mark.asyncio
async def test_manual_flush_clears_buffer(event, batcher):
	"""Проверяет, что flush() отправляет накопленные события и очищает буфер."""
	for _ in range(5):
		await batcher.add(event)

	assert len(batcher._buffer) == 5
	await batcher.flush()
	assert len(batcher._buffer) == 0

	# Повторный flush на пустом буфере не должен падать
	await batcher.flush()
	assert len(batcher._buffer) == 0

@pytest.mark.asyncio
async def test_start_kill(event, batcher):
	"""Проверка логики запуска и выключения батчера."""
	await batcher.add(event)
	assert batcher._worker_task is not None

	await batcher.kill()
	
	await asyncio.sleep(0) #Время, чтобы завершиться
	assert batcher._worker_task is None or batcher._worker_task.done()

	assert len(batcher._buffer) == 0