from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
import app.keyboards as kb
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.group import Group
from app.utils import get_current_user
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
rt = Router()


class HomeWork(StatesGroup):
    date = State()


@rt.message(Command('create_group'))
async def create_group(message: Message, command: CommandObject, session: AsyncSession):
    # Получаем текущего пользователя
    current_user = await get_current_user(session, message)

    # Проверка наличия пользователя и его прав
    if not current_user:
        await message.answer("Ошибка: Пользователь не найден")
        return

    if not current_user.is_teacher():
        await message.answer("Ошибка: Только учителя могут создавать группы")
        return

    # Проверка наличия аргумента (названия группы)
    if not command.args or not command.args.strip():
        await message.answer("Ошибка: Укажите название группы\nПример: /create_group Математика-101")
        return

    name_group = command.args.strip()

    # Проверка уникальности имени группы
    existing_group = await session.scalar(
        select(Group).where(Group.name == name_group)
    )
    if existing_group:
        await message.answer(f"Ошибка: Группа с названием '{name_group}' уже существует")
        return

    try:
        group = Group(name=name_group, author=current_user)
        # Сохраняем в БД
        session.add(group)
        await session.commit()

        await message.answer(f'✅ Группа "{name_group}" успешно создана!')

    except Exception as e:
        await session.rollback()
        await message.answer(f"⚠️ Ошибка при создании группы: {str(e)}")


@rt.message(Command('send_homework'))
async def send_homework(message: Message, state: FSMContext):
    await state.set_state(HomeWork.date)
    await message.answer('напишите на какую дату вы хотите задать домашнее задание?\nПример ввода: 23.09')


@rt.message(HomeWork.date)
async def homework_date(message: Message, state: FSMContext):
    ...
