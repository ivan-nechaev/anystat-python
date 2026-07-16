"""Configuration: flags, AnystatConfig and the ANYSTAT_API_KEY env var.

There are three equivalent ways to configure the client:

	# 1. Keyword arguments
	anystat = Anystat(api_key="...", debug=True, track_messages=True)

	# 2. A config object
	config = AnystatConfig(debug=True, track_messages=True)
	anystat = Anystat(api_key="...", config=config)

	# 3. Mixed — keyword arguments override the config
	anystat = Anystat(api_key="...", config=config, debug=False)

If `api_key` is omitted, the client reads the ANYSTAT_API_KEY environment
variable — so a bare `Anystat()` is enough (this example does exactly that).

Available flags (defaults):

	debug=False                 log everything the SDK collects and sends
	track_start=True            auto-track /start and its deep-link parameter
	track_command=True          auto-track all other commands
	track_callback_query=True   auto-track inline button clicks
	track_messages=False        auto-track text messages, INCLUDING their text

`track_messages` is the only opt-in flag: message text is never collected
unless you enable it explicitly. This example enables it so you can see the
difference — flip it back to False and watch the events being skipped in
the debug log instead.

Run:
	export BOT_TOKEN="123456:ABC..."     # from @BotFather
	export ANYSTAT_API_KEY="..."         # from https://anystat.me
	python examples/03_configuration.py
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from anystat import Anystat, AnystatConfig, setup_anystat

BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
	await message.answer(
		"Configuration demo. Send me any text — with track_messages=True "
		"the message (including its text) shows up as an event."
	)


@dp.message(F.text)
async def text_handler(message: Message) -> None:
	await message.answer("Got it! Check the console: this message was captured.")


async def main() -> None:
	logging.basicConfig(level=logging.INFO)

	if not BOT_TOKEN or not os.getenv("ANYSTAT_API_KEY"):
		raise SystemExit("Set the BOT_TOKEN and ANYSTAT_API_KEY environment variables first.")

	bot = Bot(token=BOT_TOKEN)

	config = AnystatConfig(
		debug=True,           # print every captured/skipped event to the console
		track_messages=True,  # PRIVACY: opt in to collecting message text
	)

	# No api_key argument — it is read from the ANYSTAT_API_KEY env var.
	anystat = Anystat(config=config)

	# `setup_anystat(dp, anystat)` is a one-line shortcut for:
	#
	#	from anystat.aiogram import AnystatMiddleware
	#	dp.update.middleware(AnystatMiddleware(anystat))
	#
	# Use the manual form if you need custom middleware ordering.
	setup_anystat(dp, anystat)

	dp.shutdown.register(anystat.close)

	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
