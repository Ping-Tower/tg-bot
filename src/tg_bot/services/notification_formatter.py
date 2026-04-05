import html

from tg_bot.messaging.models import TelegramNotificationMessage


def format_notification_text(notification: TelegramNotificationMessage) -> str:
    severity_icon = {
        "info": "ℹ️",
        "warning": "🟠",
        "critical": "🔴",
    }.get(notification.severity, "ℹ️")

    title = html.escape(notification.title)
    message = html.escape(notification.message)
    return f"{severity_icon} <b>{title}</b>\n\n{message}"
