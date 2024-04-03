from aiogram.types import Message, TelegramObject, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
import datetime


class TrafficMessageMiddleware(BaseMiddleware):
    time_updates: dict[int, datetime.datetime] = {}
    timedelta_limiter: datetime.timedelta = datetime.timedelta(seconds=3)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            if user_id in self.time_updates.keys():
                if (datetime.datetime.now() - self.time_updates[user_id]) > self.timedelta_limiter:
                    self.time_updates[user_id] = datetime.datetime.now()
                    return await handler(event, data)
            else:
                self.time_updates[user_id] = datetime.datetime.now()
                return await handler(event, data)
