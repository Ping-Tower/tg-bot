from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.config.settings import Settings
from tg_bot.messaging.models import TelegramInlineButton, TelegramNotificationMessage


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


def build_notification_keyboard(notification: TelegramNotificationMessage) -> InlineKeyboardMarkup | None:
    rows: list[list[InlineKeyboardButton]] = []

    for source_row in notification.inline_buttons:
        row = build_button_row(source_row)
        if row:
            rows.append(row)

    if not rows:
        return None

    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_button_row(source_row: list[TelegramInlineButton]) -> list[InlineKeyboardButton]:
    row: list[InlineKeyboardButton] = []

    for button in source_row:
        if button.url:
            row.append(InlineKeyboardButton(text=button.text, url=button.url))
            continue

        if button.callback_data:
            row.append(InlineKeyboardButton(text=button.text, callback_data=button.callback_data))

    return row
