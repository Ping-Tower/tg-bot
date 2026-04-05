from pydantic import BaseModel, ConfigDict, Field


class TelegramInlineButton(BaseModel):
    text: str
    url: str | None = None
    callback_data: str | None = Field(default=None, alias="callbackData")


class TelegramNotificationMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chat_id: int = Field(alias="chatId")
    text: str
    inline_buttons: list[list[TelegramInlineButton]] = Field(default_factory=list, alias="inlineButtons")
