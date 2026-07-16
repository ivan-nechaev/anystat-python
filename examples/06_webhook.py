"""Webhook deployment (aiohttp) with graceful event flushing.

Long polling is great for development; production bots often run behind a
webhook. Anystat needs nothing special here — the one important line is:

	dp.shutdown.register(anystat.close)

Events are batched in memory (up to 30 events or every 60 seconds), so on
redeploys and restarts you want the buffer flushed before the process dies.
`setup_application()` wires the dispatcher's startup/shutdown hooks into
the aiohttp app lifecycle, which makes that flush happen automatically on
SIGTERM / Ctrl+C.

Run:
	export BOT_TOKEN="123456:ABC..."               # from @BotFather
	export ANYSTAT_API_KEY="..."                   # from https://anystat.me
	export WEBHOOK_BASE_URL="https://example.com"  # public HTTPS url of this host
	export WEBHOOK_SECRET="some-random-string"     # optional but recommended
	python examples/06_webhook.py

For local testing you can expose the port with a tunnel (ngrok, cloudflared)
and use the tunnel URL as WEBHOOK_BASE_URL.
"""

import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from anystat import Anystat, setup_anystat

BOT_TOKEN = os.getenv("BOT_TOKEN")
ANYSTAT_API_KEY = os.getenv("ANYSTAT_API_KEY")

WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL")
WEBHOOK_PATH = "/telegram/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
	await message.answer("Webhook bot with Anystat is up and running!")


async def on_startup(bot: Bot) -> None:
	await bot.set_webhook(f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


def main() -> None:
	logging.basicConfig(level=logging.INFO)

	if not BOT_TOKEN or not ANYSTAT_API_KEY or not WEBHOOK_BASE_URL:
		raise SystemExit(
			"Set the BOT_TOKEN, ANYSTAT_API_KEY and WEBHOOK_BASE_URL environment variables first."
		)

	bot = Bot(token=BOT_TOKEN)

	anystat = Anystat(api_key=ANYSTAT_API_KEY)
	setup_anystat(dp, anystat)

	dp.startup.register(on_startup)
	# Flush buffered events when the app stops (SIGTERM, Ctrl+C, redeploy).
	dp.shutdown.register(anystat.close)

	app = web.Application()
	SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(
		app, path=WEBHOOK_PATH
	)
	setup_application(app, dp, bot=bot)

	web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
	main()
