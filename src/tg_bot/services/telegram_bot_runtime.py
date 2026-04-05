import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from faststream.rabbit import RabbitBroker

from tg_bot.config.settings import Settings
from tg_bot.messaging.models import TelegramNotificationMessage
from tg_bot.telegram.handlers import build_router
from tg_bot.telegram.keyboards import build_notification_keyboard


logger = logging.getLogger(__name__)


class TelegramBotRuntime:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.dispatcher = Dispatcher()
        self.dispatcher.include_router(build_router(settings))
        self.broker = RabbitBroker(settings.rabbitmq_url)
        self._register_subscribers()

    def _register_subscribers(self) -> None:
        @self.broker.subscriber(self.settings.rabbitmq_queue)
        async def handle_notification(message: TelegramNotificationMessage) -> None:
            await self.send_notification(message)

    async def start(self) -> None:
        await self.broker.start()
        await self.bot.set_webhook(
            url=self.settings.webhook_url,
            secret_token=self.settings.webhook_secret,
            allowed_updates=self.dispatcher.resolve_used_update_types(),
        )
        logger.info("Telegram webhook configured: %s", self.settings.webhook_url)

    async def stop(self) -> None:
        await self.bot.delete_webhook(drop_pending_updates=False)
        await self.broker.stop()
        await self.bot.session.close()

    async def send_notification(self, notification: TelegramNotificationMessage) -> None:
        keyboard = build_notification_keyboard(notification)

        await self.bot.send_message(
            chat_id=notification.chat_id,
            text=notification.text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
