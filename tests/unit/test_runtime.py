import unittest
from unittest.mock import AsyncMock

from tg_bot.messaging.models import TelegramNotificationMessage
from tg_bot.services.telegram_bot_runtime import TelegramBotRuntime


class TelegramBotRuntimeTests(unittest.IsolatedAsyncioTestCase):
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
