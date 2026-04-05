# tg-bot

Telegram notification worker for PingTower.

## Stack

- `uv`
- `FastStream` with RabbitMQ
- `aiogram`
- Telegram webhooks
- `pydantic-settings`

## Run

```bash
uv sync
cp .env.example .env
uv run tg-bot
```

## What it does

- consumes notification commands from `telegramQueue`
- sends ready-made Telegram messages from the queue using `text + inlineButtons`
- serves a webhook endpoint for Telegram updates
- handles `/start` with two buttons:
  - website
  - GitHub
