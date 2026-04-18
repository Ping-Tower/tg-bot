from contextlib import asynccontextmanager
from typing import Annotated

from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request, Response

from tg_bot.config.settings import Settings
from tg_bot.services.telegram_bot_runtime import TelegramBotRuntime


async def _healthz() -> dict[str, str]:
    return {"status": "ok"}


def _build_webhook_handler(settings: Settings, runtime: TelegramBotRuntime):
    async def handle(
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

    return handle


def create_app() -> FastAPI:
    settings = Settings()
    runtime = TelegramBotRuntime(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        async with runtime.run():
            yield

    app = FastAPI(title="PingTower tg-bot", lifespan=lifespan)
    app.state.settings = settings
    app.state.runtime = runtime
    app.add_api_route("/healthz", _healthz, methods=["GET"])

    if settings.mode == "webhook":
        app.add_api_route(
            settings.webhook_path,
            _build_webhook_handler(settings, runtime),
            methods=["POST"],
        )

    return app


app = create_app()
