import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from faststream.rabbit import RabbitBroker, RabbitQueue

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
            session=self._build_bot_session(),
        )
        self.dispatcher = Dispatcher()
        self.dispatcher.include_router(build_router(settings))
        self.broker = RabbitBroker(settings.rabbitmq_url)
        self._register_subscribers()

    def _build_bot_session(self) -> AiohttpSession:
        if self.settings.proxy_url:
            logger.info("Telegram bot will use proxy: %s", self.settings.proxy_url)
            return AiohttpSession(proxy=self.settings.proxy_url)

        return AiohttpSession()

    def _register_subscribers(self) -> None:
        queue = RabbitQueue(
            self.settings.rabbitmq_queue,
            durable=True,
            auto_delete=False,
        )

        @self.broker.subscriber(queue)
        async def handle_notification(message: TelegramNotificationMessage) -> None:
            await self.send_notification(message)

    @asynccontextmanager
    async def run(self) -> AsyncGenerator[None, None]:
        await self.broker.start()
        polling_task: asyncio.Task | None = None

        if self.settings.mode == "webhook":
            await self.bot.set_webhook(
                url=self.settings.webhook_url,
                secret_token=self.settings.webhook_secret,
                allowed_updates=self.dispatcher.resolve_used_update_types(),
            )
            logger.info("Telegram webhook configured: %s", self.settings.webhook_url)
        else:
            await self.bot.delete_webhook(drop_pending_updates=False)
            polling_task = asyncio.create_task(
                self.dispatcher.start_polling(self.bot, handle_signals=False)
            )
            logger.info("Telegram bot started in polling mode")

        try:
            yield
        finally:
            if polling_task is not None:
                polling_task.cancel()
                with suppress(asyncio.CancelledError):
                    await polling_task
            if self.settings.mode == "webhook":
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
