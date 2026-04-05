from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.config.settings import Settings
from tg_bot.messaging.models import TelegramNotificationMessage


def build_start_keyboard(settings: Settings) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=settings.start_web_button_text,
                    url=settings.web_app_url,
                ),
                InlineKeyboardButton(
                    text=settings.start_github_button_text,
                    url=settings.github_url,
                ),
            ]
        ]
    )


def build_notification_keyboard(
    settings: Settings,
    notification: TelegramNotificationMessage,
) -> InlineKeyboardMarkup:
    server_url = notification.metadata.get("serverUrl")
    if not isinstance(server_url, str) or not server_url.strip():
        server_url = settings.build_server_url(notification.server_id)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=settings.server_button_text,
                    url=server_url,
                )
            ]
        ]
    )
