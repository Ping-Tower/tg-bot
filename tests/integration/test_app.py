import importlib
import os
import sys
import unittest
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient


TEST_ENV = {
    "TG_BOT_BOT_TOKEN": "123456:TEST_TOKEN",
    "TG_BOT_WEBHOOK_BASE_URL": "https://bot.example.com",
    "TG_BOT_WEBHOOK_PATH": "/webhooks/telegram",
    "TG_BOT_WEBHOOK_SECRET": "super-secret",
    "TG_BOT_WEB_APP_URL": "https://app.example.com",
    "TG_BOT_GITHUB_URL": "https://github.com/example/PingTower",
}


@dataclass
class FakeDispatcher:
    calls: list[tuple[object, object]] = field(default_factory=list)

    async def feed_update(self, bot: object, update: object) -> None:
        self.calls.append((bot, update))


@dataclass
class FakeRuntime:
    bot: object = field(default_factory=object)
    dispatcher: FakeDispatcher = field(default_factory=FakeDispatcher)
    started: bool = False
    stopped: bool = False

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.stopped = True


class AppIntegrationTests(unittest.TestCase):
    def test_healthz_uses_lifespan_and_returns_ok(self) -> None:
        app, runtime = build_test_app()

        with TestClient(app) as client:
            response = client.get("/healthz")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json())
        self.assertTrue(runtime.started)
        self.assertTrue(runtime.stopped)

    def test_webhook_rejects_invalid_secret(self) -> None:
        app, runtime = build_test_app()

        with TestClient(app) as client:
            response = client.post(
                "/webhooks/telegram",
                headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
                json=build_update_payload(),
            )

        self.assertEqual(401, response.status_code)
        self.assertEqual({"detail": "Invalid Telegram webhook secret"}, response.json())
        self.assertEqual([], runtime.dispatcher.calls)

    def test_webhook_accepts_valid_update_and_forwards_to_dispatcher(self) -> None:
        app, runtime = build_test_app()

        with TestClient(app) as client:
            response = client.post(
                "/webhooks/telegram",
                headers={"X-Telegram-Bot-Api-Secret-Token": "super-secret"},
                json=build_update_payload(),
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(runtime.dispatcher.calls))

        bot, update = runtime.dispatcher.calls[0]
        self.assertIs(bot, runtime.bot)
        self.assertEqual(1, update.update_id)
        self.assertEqual("/start", update.message.text)


def build_test_app() -> tuple[Any, FakeRuntime]:
    runtime = FakeRuntime()
    runtime_module = importlib.import_module("tg_bot.services.telegram_bot_runtime")

    with patch.dict(os.environ, TEST_ENV, clear=False):
        with patch.object(runtime_module, "TelegramBotRuntime", side_effect=lambda settings: runtime):
            sys.modules.pop("tg_bot.app", None)
            app_module = importlib.import_module("tg_bot.app")
            return app_module.app, runtime


def build_update_payload() -> dict[str, Any]:
    return {
        "update_id": 1,
        "message": {
            "message_id": 10,
            "date": 1_712_311_111,
            "chat": {
                "id": 123456789,
                "type": "private",
                "first_name": "Ivan",
            },
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Ivan",
            },
            "text": "/start",
        },
    }
