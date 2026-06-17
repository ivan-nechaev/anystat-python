import asyncio
from typing import Generic, TypeVar

T = TypeVar("T")

class AnystatBatcher(Generic[T]):
	"""
	Async batcher for Anystat events.

	It accumulates events and sends them in batches instead of one by one.
	You can control batching behavior using two parameters:
	max_batch_size and flush_interval.

	The batcher automatically flushes events when the buffer is full or
	when the time interval has passed.
	"""

	def __init__(self, max_batch_size: int, flush_interval: float):
		self._buffer: list[T] = []
		self._running = True
		self._lock = asyncio.Lock()
		self._max_batch_size = max_batch_size 
		self._flush_interval = flush_interval
		self._worker_task: asyncio.Task | None = None

	async def add(self, item: T):
		if self._worker_task is None:
			self._worker_task = asyncio.create_task(self._worker())

		async with self._lock:
			self._buffer.append(item)

			if len(self._buffer) >= self._max_batch_size:
				batch = self._buffer
				self._buffer = []
			else:
				batch = []

		await self._flush_batch(batch)	


	async def _worker(self) -> None:
		while self._running:
			await asyncio.sleep(self._flush_interval)
			if len(self._buffer) < 1: continue
			
			await self.flush()

			
	
	async def kill(self) -> None:
		self._running = False
		if self._worker_task:
			self._worker_task.cancel()
		
		await self.flush()


	async def _flush_batch(self, batch: list[T]) -> None:
		if not batch:
			return None
		
		print(f'Отправил {len(batch)} событий на сервер') # TODO: Здесь надо отправить

	async def flush(self) -> None:
		async with self._lock:
			if not self._buffer:
				return None
			batch = self._buffer
			self._buffer = []
		await self._flush_batch(batch)