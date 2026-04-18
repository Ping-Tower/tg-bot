import uvicorn

from tg_bot.app import app


def main() -> None:
    settings = app.state.settings
    uvicorn.run(app, host=settings.host, port=settings.port)