import unittest
from unittest.mock import AsyncMock, Mock, patch

from faststream.rabbit import RabbitQueue

from tg_bot.config.settings import Settings
from tg_bot.messaging.models import TelegramNotificationMessage
from tg_bot.services.telegram_bot_runtime import TelegramBotRuntime


class TelegramBotRuntimeTests(unittest.IsolatedAsyncioTestCase):
    def test_build_bot_session_uses_direct_connection_by_default(self) -> None:
        runtime = object.__new__(TelegramBotRuntime)
        runtime.settings = Settings.model_validate(
            {
                "bot_token": "123456:TEST_TOKEN",
                "mode": "polling",
                "proxy_url": None,
                "web_app_url": "https://app.example.com",
                "github_url": "https://github.com/example/PingTower",
            }
        )

        with patch("tg_bot.services.telegram_bot_runtime.AiohttpSession") as session_cls:
            TelegramBotRuntime._build_bot_session(runtime)

        session_cls.assert_called_once_with()

    def test_build_bot_session_passes_proxy_url_to_aiohttp_session(self) -> None:
        runtime = object.__new__(TelegramBotRuntime)
        runtime.settings = Settings.model_validate(
            {
                "bot_token": "123456:TEST_TOKEN",
                "mode": "polling",
                "proxy_url": "socks5://user:password@127.0.0.1:1080",
                "web_app_url": "https://app.example.com",
                "github_url": "https://github.com/example/PingTower",
            }
        )

        with patch("tg_bot.services.telegram_bot_runtime.AiohttpSession") as session_cls:
            TelegramBotRuntime._build_bot_session(runtime)

        session_cls.assert_called_once_with(proxy="socks5://user:password@127.0.0.1:1080")

    def test_register_subscribers_declares_durable_queue(self) -> None:
        runtime = object.__new__(TelegramBotRuntime)
        runtime.settings = Settings.model_validate(
            {
                "bot_token": "123456:TEST_TOKEN",
                "mode": "polling",
                "rabbitmq_queue": "telegramQueue",
                "proxy_url": None,
                "web_app_url": "https://app.example.com",
                "github_url": "https://github.com/example/PingTower",
            }
        )
        runtime.broker = Mock()
        runtime.broker.subscriber.side_effect = lambda queue: (lambda handler: handler)

        TelegramBotRuntime._register_subscribers(runtime)

        runtime.broker.subscriber.assert_called_once()
        queue = runtime.broker.subscriber.call_args.args[0]
        self.assertIsInstance(queue, RabbitQueue)
        self.assertEqual("telegramQueue", queue.name)
        self.assertTrue(queue.durable)
        self.assertFalse(queue.auto_delete)

    async def test_send_notification_passes_ready_text_and_keyboard_to_bot(self) -> None:
        runtime = object.__new__(TelegramBotRuntime)
        runtime.bot = AsyncMock()

        notification = TelegramNotificationMessage.model_validate(
            {
                "chatId": 123456789,
                "text": "🔴 <b>Внимание!</b>\nСервер <b>DB</b> недоступен.",
                "inlineButtons": [
                    [
                        {"text": "Dashboard", "url": "https://app.example.com/servers/123"},
                        {"text": "Ack", "callbackData": "ack_123"},
                    ]
                ],
            }
        )

        await TelegramBotRuntime.send_notification(runtime, notification)

        runtime.bot.send_message.assert_awaited_once()
        _, kwargs = runtime.bot.send_message.await_args
        self.assertEqual(123456789, kwargs["chat_id"])
        self.assertEqual(notification.text, kwargs["text"])
        self.assertTrue(kwargs["disable_web_page_preview"])
        self.assertIsNotNone(kwargs["reply_markup"])
        self.assertEqual("Dashboard", kwargs["reply_markup"].inline_keyboard[0][0].text)
        self.assertEqual("ack_123", kwargs["reply_markup"].inline_keyboard[0][1].callback_data)

    async def test_send_notification_omits_reply_markup_when_buttons_absent(self) -> None:
        runtime = object.__new__(TelegramBotRuntime)
        runtime.bot = AsyncMock()

        notification = TelegramNotificationMessage.model_validate(
            {
                "chatId": 123456789,
                "text": "hello",
                "inlineButtons": [],
            }
        )

        await TelegramBotRuntime.send_notification(runtime, notification)

        runtime.bot.send_message.assert_awaited_once()
        _, kwargs = runtime.bot.send_message.await_args
        self.assertIsNone(kwargs["reply_markup"])
