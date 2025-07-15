from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database import get_db
import os
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User


bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())

# Middleware для инъекции сессии БД


class DatabaseMiddleware:
    def __init__(self):
        pass

    async def __call__(self, handler, event, data):
        async for session in get_db():
            data["session"] = session
            return await handler(event, data)


class UserUpdaterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем сессию из данных
        session: AsyncSession = data["session"]

        # Получаем информацию о пользователе из события
        from_user = None
        if hasattr(event, 'from_user'):
            from_user = event.from_user
        elif hasattr(event, 'message') and event.message:
            from_user = event.message.from_user

        if not from_user:
            return await handler(event, data)

        # Обновляем данные пользователя в базе
        await update_user_info(
            telegram_id=from_user.id,
            username=from_user.username,
            session=session
        )

        return await handler(event, data)


async def update_user_info(
    telegram_id: int,
    username: str | None,
    session: AsyncSession
):
    # Проверяем существование пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Создаем нового пользователя, если не найден
        new_user = User(
            telegram_id=telegram_id,
            username=username,
        )
        session.add(new_user)
    else:
        # Обновляем данные, если они изменились
        if (user.username != username):

            await session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(
                    username=username,
                )
            )

    await session.commit()


dp.update.middleware(DatabaseMiddleware())
dp.update.middleware(UserUpdaterMiddleware())
