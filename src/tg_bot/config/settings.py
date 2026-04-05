from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TG_BOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    webhook_base_url: str
    webhook_path: str = "/webhooks/telegram"
    webhook_secret: str | None = None

    host: str = "0.0.0.0"
    port: int = 8080

    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_queue: str = "telegramQueue"

    web_app_url: str
    github_url: str

    start_message_text: str = "TODO: replace this /start text."
    start_web_button_text: str = "Open Web"
    start_github_button_text: str = "GitHub"

    @computed_field(return_type=str)
    @property
    def webhook_url(self) -> str:
        path = self.webhook_path if self.webhook_path.startswith("/") else f"/{self.webhook_path}"
        return f"{self.webhook_base_url.rstrip('/')}{path}"
