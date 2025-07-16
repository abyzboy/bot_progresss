from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.group import Group


async def get_current_user(session: AsyncSession, message: Message) -> User:
    return (await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )).scalar_one_or_none()


async def get_groups(session: AsyncSession):
    result = await session.execute(select(Group))
    groups = result.scalars().all()
    return groups
