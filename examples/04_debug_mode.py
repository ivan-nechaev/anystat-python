"""Debug mode: see exactly what leaves your bot.

With `debug=True` the SDK logs, through the standard `logging` module
(logger name: "anystat"):

- every captured event with its exact payload,
- every skipped event and the reason it was skipped,
- every HTTP request to the Anystat API and its outcome.

Sample output:

	[anystat] endpoint: https://api.anystat.me | api key: any_…7f2c
	[anystat] auto-tracking: /start=on commands=on callbacks=on messages=off
	[anystat] capture start_command via AnystatMiddleware:
	{
	  "event_type": "start_command",
	  "user_id": 12345,
	  "received_at": 1767225600,
	  "duration": 12,
	  "message_id": 42,
	  "start_param": "campaign_x"
	}
	[anystat] skip message from user=12345 (track_messages=off, text not collected)
	[anystat] → POST /v1/collect/events (2 events)

How it plays with your logging setup:

- If your app has already configured logging (like this example does),
  Anystat respects your handlers and formatting.
- If not, it installs a minimal `[anystat]` console handler for you.
- The check happens when the client is created, so configure logging
  BEFORE calling `Anystat(...)`.
- To quiet the SDK later without touching your config:

	logging.getLogger("anystat").setLevel(logging.WARNING)

Try it: send /start, then another command, then plain text — and watch
which events are captured and which are skipped (and why).

Run:
	export BOT_TOKEN="123456:ABC..."     # from @BotFather
	export ANYSTAT_API_KEY="..."         # from https://anystat.me
	python examples/04_debug_mode.py
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
	await message.answer(
		"Debug demo. Try a command (/whatever) and a plain text message, "
		"then look at the console."
	)


@dp.message()
async def any_message_handler(message: Message) -> None:
	await message.answer("Now check the console output.")


async def main() -> None:
	# Configure logging FIRST — Anystat will plug into it.
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s %(name)s %(levelname)s: %(message)s",
	)

	if not BOT_TOKEN or not ANYSTAT_API_KEY:
		raise SystemExit("Set the BOT_TOKEN and ANYSTAT_API_KEY environment variables first.")

	bot = Bot(token=BOT_TOKEN)

	anystat = Anystat(api_key=ANYSTAT_API_KEY, debug=True)
	setup_anystat(dp, anystat)

	dp.shutdown.register(anystat.close)

	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
