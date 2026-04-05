from contextlib import asynccontextmanager
from typing import Annotated

from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request, Response

from tg_bot.config.settings import Settings
from tg_bot.services.telegram_bot_runtime import TelegramBotRuntime


def create_app() -> FastAPI:
    settings = Settings()
    runtime = TelegramBotRuntime(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await runtime.start()
        try:
            yield
        finally:
            await runtime.stop()

    app = FastAPI(title="PingTower tg-bot", lifespan=lifespan)
    app.state.settings = settings
    app.state.runtime = runtime

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(settings.webhook_path)
    async def telegram_webhook(
        request: Request,
        secret_token: Annotated[
            str | None,
            Header(alias="X-Telegram-Bot-Api-Secret-Token"),
        ] = None,
    ) -> Response:
        if settings.webhook_secret and secret_token != settings.webhook_secret:
            raise HTTPException(status_code=401, detail="Invalid Telegram webhook secret")

        update = Update.model_validate(await request.json(), context={"bot": runtime.bot})
        await runtime.dispatcher.feed_update(runtime.bot, update)
        return Response(status_code=200)

    return app


app = create_app()
