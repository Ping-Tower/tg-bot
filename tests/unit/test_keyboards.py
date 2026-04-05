import unittest

from tg_bot.config.settings import Settings
from tg_bot.messaging.models import TelegramNotificationMessage
from tg_bot.telegram.keyboards import build_notification_keyboard, build_start_keyboard


class KeyboardTests(unittest.TestCase):
    def test_build_start_keyboard_uses_configured_links(self) -> None:
        settings = Settings(
            bot_token="token",
            webhook_base_url="https://bot.example.com",
            web_app_url="https://app.example.com",
            github_url="https://github.com/example/PingTower",
        )

        keyboard = build_start_keyboard(settings)

        self.assertEqual(1, len(keyboard.inline_keyboard))
        self.assertEqual(2, len(keyboard.inline_keyboard[0]))
        self.assertEqual("https://app.example.com", keyboard.inline_keyboard[0][0].url)
        self.assertEqual("https://github.com/example/PingTower", keyboard.inline_keyboard[0][1].url)

    def test_build_notification_keyboard_supports_url_and_callback_buttons(self) -> None:
        notification = TelegramNotificationMessage.model_validate(
            {
                "chatId": 123456789,
                "text": "test",
                "inlineButtons": [
                    [
                        {"text": "Dashboard", "url": "https://app.example.com/servers/123"},
                        {"text": "Ack", "callbackData": "ack_123"},
                    ]
                ],
            }
        )

        keyboard = build_notification_keyboard(notification)

        self.assertIsNotNone(keyboard)
        self.assertEqual(1, len(keyboard.inline_keyboard))
        self.assertEqual(2, len(keyboard.inline_keyboard[0]))
        self.assertEqual("Dashboard", keyboard.inline_keyboard[0][0].text)
        self.assertEqual("https://app.example.com/servers/123", keyboard.inline_keyboard[0][0].url)
        self.assertEqual("Ack", keyboard.inline_keyboard[0][1].text)
        self.assertEqual("ack_123", keyboard.inline_keyboard[0][1].callback_data)

    def test_build_notification_keyboard_returns_none_for_empty_rows(self) -> None:
        notification = TelegramNotificationMessage.model_validate(
            {
                "chatId": 123456789,
                "text": "test",
                "inlineButtons": [[{"text": "Broken"}]],
            }
        )

        keyboard = build_notification_keyboard(notification)

        self.assertIsNone(keyboard)
