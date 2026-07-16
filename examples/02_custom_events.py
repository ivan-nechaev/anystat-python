"""Custom events: track anything that matters with `anystat.track()`.

A tiny "coffee shop" bot:

- /menu shows an inline keyboard — button clicks are auto-tracked as
  `callback_query` events, nothing to do on your side;
- pressing a button "sells" a drink and sends a custom `purchase` event
  with properties;
- a system event with `user_id=None` is sent once on startup.

`track(name, user_id, **properties)` — the first argument is the event
name, the second is the user ID (or None for system events). Any extra
keyword arguments become event properties; pass anything JSON-serializable.

The client is shared with handlers through the dispatcher's workflow data
(`dp["anystat"] = anystat`), the idiomatic aiogram 3 way to avoid globals.

Run:
	export BOT_TOKEN="123456:ABC..."     # from @BotFather
	export ANYSTAT_API_KEY="..."         # from https://anystat.me
	python examples/02_custom_events.py
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from anystat import Anystat, setup_anystat

BOT_TOKEN = os.getenv("BOT_TOKEN")
ANYSTAT_API_KEY = os.getenv("ANYSTAT_API_KEY")

MENU = {
	"espresso": 2.00,
	"latte": 3.50,
	"raf": 4.00,
}

dp = Dispatcher()


def menu_keyboard() -> InlineKeyboardMarkup:
	rows = [
		[InlineKeyboardButton(text=f"{name.title()} — ${price:.2f}", callback_data=f"buy:{name}")]
		for name, price in MENU.items()
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
	await message.answer("Welcome to the coffee shop! Send /menu to order.")


@dp.message(Command("menu"))
async def menu_handler(message: Message, anystat: Anystat) -> None:
	await message.answer("What would you like?", reply_markup=menu_keyboard())

	# A custom funnel step: the user has seen the menu.
	await anystat.track("menu_opened", user_id=message.from_user.id if message.from_user else None)


@dp.callback_query(F.data.startswith("buy:"))
async def buy_handler(callback: CallbackQuery, anystat: Anystat) -> None:
	# The button click itself is already auto-tracked as `callback_query`.
	item = (callback.data or "").split(":", 1)[1]
	price = MENU.get(item)
	if price is None:
		await callback.answer("This item is no longer on the menu.")
		return

	# ... your payment / order logic goes here ...

	await anystat.track(
		"purchase",
		user_id=callback.from_user.id,
		item=item,
		price=price,
		currency="USD",
	)

	await callback.answer(f"One {item} coming up!")
	if callback.message:
		await callback.message.answer(f"You bought a {item} for ${price:.2f}. Enjoy!")


async def on_startup(anystat: Anystat) -> None:
	# System events are not tied to a user — pass user_id=None.
	await anystat.track("bot_started", None, example="02_custom_events")


async def main() -> None:
	logging.basicConfig(level=logging.INFO)

	if not BOT_TOKEN or not ANYSTAT_API_KEY:
		raise SystemExit("Set the BOT_TOKEN and ANYSTAT_API_KEY environment variables first.")

	bot = Bot(token=BOT_TOKEN)

	anystat = Anystat(api_key=ANYSTAT_API_KEY, debug=True)
	setup_anystat(dp, anystat)
	dp["anystat"] = anystat  # inject into handlers that declare `anystat: Anystat`

	dp.startup.register(on_startup)
	dp.shutdown.register(anystat.close)

	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
