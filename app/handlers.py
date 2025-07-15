from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
import app.keyboards as kb
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from app.utils import get_current_user
rt = Router()


@rt.message(Command('add_teacher'))
async def add_teacher(message: Message, command: CommandObject, session: AsyncSession):
    current_user = await get_current_user(session, message)
    if current_user.is_admin():
        username = command.args[1:]
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user:
            user.role = 'teacher'
            await session.commit()
            await message.answer(f'Учитель {username} был добавлен')
        else:
            await message.answer('Данного пользователя нет в базе данных, он сначало должен зарегестрироваться')

    else:
        await message.answer("❌ Недостаточно прав")


@rt.message(CommandStart())
async def cmd_start(message: types.Message, session: AsyncSession):
    # Проверяем существование пользователя
    user = await get_current_user(session, message)

    # Создаем нового пользователя если не найден
    if not user:
        new_user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username
        )
        session.add(new_user)
        await session.commit()
        await message.answer("Вы зарегистрированы!")
    else:
        await message.answer("С возвращением!")


@rt.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Бот ничего не умеет', reply_markup=kb.main)
