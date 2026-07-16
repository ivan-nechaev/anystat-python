"""Quickstart: the two-line Anystat integration.

A minimal echo bot with analytics. `setup_anystat()` attaches a single
middleware to the dispatcher and auto-tracking starts immediately:

- /start commands (including the deep-link parameter),
- all other commands,
- inline button clicks (callback queries),
- bot blocked / unblocked by a user.

No changes to your handlers are required.

Run:
	export BOT_TOKEN="123456:ABC..."     # from @BotFather
	export ANYSTAT_API_KEY="..."         # from https://anystat.me
	python examples/01_quickstart.py
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from anystat import Anystat, setup_anystat

BOT_TOKEN = os.getenv("BOT_TOKEN")
ANYSTAT_API_KEY = os.getenv("ANYSTAT_API_KEY")

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
	await message.answer("Hi! Send me anything and I will echo it back.")


@dp.message()
async def echo_handler(message: Message) -> None:
	await message.answer(message.text or "I can only echo text, sorry.")


async def main() -> None:
	logging.basicConfig(level=logging.INFO)

	if not BOT_TOKEN or not ANYSTAT_API_KEY:
		raise SystemExit("Set the BOT_TOKEN and ANYSTAT_API_KEY environment variables first.")

	bot = Bot(token=BOT_TOKEN)

	anystat = Anystat(api_key=ANYSTAT_API_KEY)  # 1. create the client
	setup_anystat(dp, anystat)                  # 2. attach the middleware

	# Flush any buffered events before the process exits.
	dp.shutdown.register(anystat.close)

	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
