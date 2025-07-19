from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject, CommandStart
import app.keyboards as kb
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.group import Group
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils import get_current_user
rt = Router()


@rt.message(Command('add_teacher'))
async def add_teacher(message: Message, command: CommandObject, session: AsyncSession):
    current_user = await get_current_user(session, message.from_user.id)
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
    user = await get_current_user(session, message.from_user.id)

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


@rt.message(Command('groups'))
async def get_groups(message: Message, session: AsyncSession):
    await message.answer(f'Выберите группу в которую хотите вступить', reply_markup=await kb.group_builder(session))


@rt.message(F.text == 'отмена')
async def process_theme(message: Message, state: FSMContext):
    await state.clear()


@rt.callback_query(F.data.startswith('group_'))
async def group_handler(callback: CallbackQuery, session: AsyncSession):
    group_name = callback.data[6:]
    group = (await session.execute(select(Group).where(Group.name == group_name))).scalar_one_or_none()
    user = await get_current_user(session, callback.from_user.id)
    if group:
        group.members.append(user)
        await session.commit()
        await callback.message.edit_text(f'Вы выбрали группу {group_name}.')
    else:
        await callback.message.edit_text(f'Данной группы не существует.')
