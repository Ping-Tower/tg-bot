from typing import Literal

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TG_BOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    mode: Literal["webhook", "polling"] = "webhook"
    webhook_base_url: str | None = None
    webhook_path: str = "/webhooks/telegram"
    webhook_secret: str | None = None

    host: str = "0.0.0.0"
    port: int = 8080

    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_queue: str = "telegramQueue"
    proxy_url: str | None = None

    web_app_url: str
    github_url: str

    start_message_text: str = "TODO: replace this /start text."
    start_web_button_text: str = "Open Web"
    start_github_button_text: str = "GitHub"

    @model_validator(mode="after")
    def validate_webhook_settings(self) -> "Settings":
        if self.mode == "webhook" and not self.webhook_base_url:
            raise ValueError("TG_BOT_WEBHOOK_BASE_URL is required when TG_BOT_MODE=webhook")
        return self

    @computed_field(return_type=str | None)
    @property
    def webhook_url(self) -> str | None:
        if not self.webhook_base_url:
            return None
        path = self.webhook_path if self.webhook_path.startswith("/") else f"/{self.webhook_path}"
        return f"{self.webhook_base_url.rstrip('/')}{path}"
