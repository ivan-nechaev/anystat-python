# Anystat

[![PyPI](https://img.shields.io/pypi/v/anystat)](https://pypi.org/project/anystat/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://pypi.org/project/anystat/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://github.com/ivan-nechaev/anystat-python/actions/workflows/ci.yml/badge.svg)](https://github.com/ivan-nechaev/anystat-python/actions/workflows/ci.yml)

[English](README.md) | Русский

**Лёгкая privacy-first аналитика для Telegram-ботов на [aiogram 3](https://github.com/aiogram/aiogram).**

Добавьте две строки кода — и узнайте, как люди на самом деле пользуются вашим ботом: источники `/start` и диплинки, использование команд, нажатия кнопок, блокировки и возвращения — всё в вашем дашборде [Anystat](https://anystat.me).

```python
anystat = Anystat(api_key="YOUR_API_KEY")
setup_anystat(dp, anystat)
```

## Почему Anystat

- **Интеграция в две строки.** Один middleware, ноль изменений в ваших хендлерах.
- **Приватность по умолчанию.** Текст сообщений *не* собирается, пока вы явно этого не включите. Данные профиля пользователей не собираются.
- **Ничего скрытого.** Включите `debug=True` — SDK логирует каждое собранное событие, каждый отправленный payload и всё, что он *пропускает*. Проверьте сами.
- **Fire and forget.** События отправляются пачками, повторяются с бэкоффом и никогда не блокируют хендлеры. Если аналитика недоступна — бот продолжает работать.
- **Полная типизация.** В пакете есть `py.typed` — автодополнение и проверка типов из коробки.

## Установка

```bash
pip install anystat
```

или через [uv](https://github.com/astral-sh/uv):

```bash
uv add anystat
```

Требуются **Python 3.12+** и **aiogram 3**.

## Быстрый старт

```python
import asyncio
from aiogram import Bot, Dispatcher
from anystat import Anystat, setup_anystat


async def main():
    bot = Bot(token="YOUR_BOT_TOKEN")
    dp = Dispatcher()

    anystat = Anystat(api_key="YOUR_ANYSTAT_API_KEY")   # 1
    setup_anystat(dp, anystat)                          # 2
    dp.shutdown.register(anystat.close)  # доотправить события при остановке

    # ... регистрируйте хендлеры как обычно ...

    await dp.start_polling(bot)


asyncio.run(main())
```

Готово. Автотрекинг работает сразу — менять хендлеры не нужно.

API-ключ можно также передать через переменную окружения `ANYSTAT_API_KEY` и создавать клиент просто как `Anystat()`.

## Что трекается

| Событие | По умолчанию | Что это даёт |
|---|---|---|
| Команда `/start` | ✅ вкл | Новые пользователи и параметры диплинков (`t.me/yourbot?start=campaign_x`) — видно, откуда приходят люди |
| Остальные команды | ✅ вкл | Какими командами реально пользуются |
| Callback-запросы | ✅ вкл | Нажатия inline-кнопок |
| Блокировка / разблокировка бота | ✅ вкл | Отток: когда пользователи блокируют бота и когда возвращаются |
| Текстовые сообщения | ❌ **выкл** | Полный текст сообщения — только по явному согласию, см. ниже |

Каждое событие содержит ID пользователя, отметку времени и длительность обработки апдейта вашим хендлером (в мс).

### Что НЕ собирается

- **Текст сообщений** — пока вы явно не укажете `track_messages=True`.
- **Данные профиля** (username, имя, язык) — сбор профилей в этой версии отключён.
- Больше ничего. Не верьте на слово — запустите с `debug=True` и посмотрите на каждый байт, который покидает вашего бота.

## Кастомные события

Трекайте всё, что важно именно вашему боту, через `track()`:

```python
from aiogram import types
from aiogram.filters import Command


@dp.message(Command("buy"))
async def buy_handler(message: types.Message):
    # ... ваша логика ...
    await anystat.track(
        "purchase",
        user_id=message.from_user.id,
        amount=99,
        currency="USD",
    )
```

Первый аргумент — имя события, второй — ID пользователя (или `None` для системных событий). Любые дополнительные именованные аргументы становятся свойствами события — подойдёт всё, что сериализуется в JSON.

## Конфигурация

Передавайте опции напрямую:

```python
anystat = Anystat(
    api_key="YOUR_API_KEY",
    track_messages=True,
    debug=True,
)
```

или сгруппируйте их в объект конфигурации:

```python
from anystat import Anystat, AnystatConfig

config = AnystatConfig(track_messages=True, debug=True)
anystat = Anystat(api_key="YOUR_API_KEY", config=config)
```

Опции, переданные напрямую в `Anystat(...)`, имеют приоритет над конфигом.

| Опция | По умолчанию | Описание |
|---|---|---|
| `debug` | `False` | Логировать всё, что SDK собирает и отправляет (см. ниже) |
| `track_start` | `True` | Автотрекинг команды `/start` и её диплинк-параметра |
| `track_command` | `True` | Автотрекинг остальных команд |
| `track_callback_query` | `True` | Автотрекинг нажатий inline-кнопок |
| `track_messages` | `False` | Автотрекинг входящих текстовых сообщений, **включая их текст** |

## Debug-режим: видно всё, что покидает вашего бота

Доверяй, но проверяй. С `debug=True` SDK логирует каждое собранное событие, каждое пропущенное (и почему) и точный payload каждого запроса:

```
[anystat] endpoint: https://api.anystat.me | api key: any_…7f2c
[anystat] auto-tracking: /start=on commands=on callbacks=on messages=off
[anystat] message text is NOT collected (track_messages=off)
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
[anystat] ← 200 in 143 ms
```

Debug-вывод идёт через стандартный модуль `logging` под логгером `"anystat"`. Если logging в приложении уже настроен, Anystat уважает ваши хендлеры и формат; если нет — сам поднимет минимальный консольный хендлер `[anystat]`.

## Надёжность

Аналитика никогда не должна быть причиной поломки бота:

- **Батчинг.** События буферизуются в памяти и отправляются пачками (до 30 событий или раз в 60 секунд), а не отдельным HTTP-запросом на каждый апдейт.
- **Ретраи.** Сетевые ошибки и повторяемые статусы (429, 5xx, …) повторяются с экспоненциальным бэкоффом и джиттером.
- **Без задержек.** Трекинг выполняется после завершения хендлера и не замедляет ответы пользователям.
- **Отказоустойчивость.** Если API Anystat недоступен после всех ретраев, события отбрасываются с предупреждением в логах — бот продолжает работать.

Вызывайте `await anystat.close()` при остановке (или зарегистрируйте его, как в быстром старте), чтобы доотправить буфер событий перед завершением процесса.

## Требования

- Python 3.12+
- aiogram >= 3.28

## Лицензия

[MIT](LICENSE)