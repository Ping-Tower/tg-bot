from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TelegramNotificationMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId")
    telegram_user_id: int = Field(alias="telegramUserId")
    server_id: str = Field(alias="serverId")
    title: str
    message: str
    severity: Literal["info", "warning", "critical"] = "info"
    metadata: dict[str, Any] = Field(default_factory=dict)
