import uvicorn

from tg_bot.app import app
from tg_bot.config.settings import Settings


def main() -> None:
    settings = Settings()
    uvicorn.run(
        "tg_bot.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
