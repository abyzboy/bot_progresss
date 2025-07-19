from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.group import Group
from models.home_work import Homework
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_current_user(session: AsyncSession, user_id) -> User:
    return (await session.execute(
        select(User).where(User.telegram_id == user_id)
    )).scalar_one_or_none()


async def get_groups(session: AsyncSession):
    result = await session.execute(select(Group))
    groups = result.scalars().all()
    return groups


async def get_student_groups(session: AsyncSession, user_id):
    user = await get_current_user(session, user_id)
    return user.groups


async def get_own_groups(session: AsyncSession, user_id):
    user = await get_current_user(session, user_id)
    return user.own_groups


async def save_homework(teacher_id, format_message, data, date, group, theme, session: AsyncSession):
    homework = Homework(teacher_id=teacher_id,
                        format_message=format_message, data=data, date=date, group=group, theme=theme)
    session.add(homework)
    await session.commit()
    return homework


async def broadcast_homework_notification(
    bot: Bot,
    session: AsyncSession,
    homework_details: str,
    group: Group,
    homework_id: int
):
    users = (await session.execute(select(User).join(User.groups).where(Group.id == group.id))).scalars().all()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Посмотреть домашнее задание",
                    callback_data=f"details_{homework_id}"
                )
            ]
        ]
    )

    for user in users:
        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=f"📚 Новое домашнее задание!\n\n{homework_details}", reply_markup=keyboard
            )
        except TelegramForbiddenError:
            # Пользователь заблокировал бота
            print(f"Пользователь {user.telegram_id} заблокировал бота")
        except Exception as e:
            print(f"Ошибка при отправке уведомления {user.telegram_id}: {e}")
