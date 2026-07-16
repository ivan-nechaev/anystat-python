"""Deep links: find out where your users come from.

Anystat auto-tracks every /start together with its deep-link parameter
(`t.me/yourbot?start=campaign_x`), so your dashboard shows which campaign,
post or QR code brought each user — with zero code on your side.

This example only adds the bot's own behavior on top:

- a handler for deep-linked starts that greets the user by campaign,
- /link, which generates a real deep link for this bot so you can test
  the whole flow yourself.

Try it: send /link, open the generated link, press Start — then find the
`start_command` event with `start_param="summer_promo"` in the debug log
and on the dashboard.

Run:
	export BOT_TOKEN="123456:ABC..."     # from @BotFather
	export ANYSTAT_API_KEY="..."         # from https://anystat.me
	python examples/05_deep_links.py
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from aiogram.utils.deep_linking import create_start_link

from anystat import Anystat, setup_anystat

BOT_TOKEN = os.getenv("BOT_TOKEN")
ANYSTAT_API_KEY = os.getenv("ANYSTAT_API_KEY")

dp = Dispatcher()


# NOTE: register the deep-link handler BEFORE the plain /start handler —
# in aiogram the first matching handler wins.
@dp.message(CommandStart(deep_link=True))
async def start_with_deep_link(message: Message, command: CommandObject) -> None:
	# Anystat has already captured this /start with its `start_param`;
	# this handler is only about what the bot replies.
	await message.answer(f"Welcome! You came here via: {command.args}")


@dp.message(CommandStart())
async def start_plain(message: Message) -> None:
	await message.answer("Welcome! Send /link to get a test deep link for this bot.")


@dp.message(Command("link"))
async def make_link(message: Message, bot: Bot) -> None:
	link = await create_start_link(bot, "summer_promo")
	await message.answer(
		"Here is a deep link, as if from an ad campaign:\n"
		f"{link}\n\n"
		"Open it and press Start — the source will appear in your analytics."
	)


async def main() -> None:
	logging.basicConfig(level=logging.INFO)

	if not BOT_TOKEN or not ANYSTAT_API_KEY:
		raise SystemExit("Set the BOT_TOKEN and ANYSTAT_API_KEY environment variables first.")

	bot = Bot(token=BOT_TOKEN)

	# debug=True so you can see the captured `start_param` in the console.
	anystat = Anystat(api_key=ANYSTAT_API_KEY, debug=True)
	setup_anystat(dp, anystat)

	dp.shutdown.register(anystat.close)

	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
