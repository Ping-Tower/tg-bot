from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from tg_bot.config.settings import Settings
from tg_bot.telegram.keyboards import build_start_keyboard


def build_router(settings: Settings) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def handle_start(message: Message) -> None:
        await message.answer(
            settings.start_message_text,
            reply_markup=build_start_keyboard(settings),
            disable_web_page_preview=True,
        )

    return router
