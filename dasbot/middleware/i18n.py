from typing import Dict, Any, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from dasbot.i18n import set_locale

class I18nMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self, handler: Any, event: Union[Message, CallbackQuery], data: Dict[str, Any]
    ) -> Any:
        set_locale(event.from_user.language_code)
        return await handler(event, data)
