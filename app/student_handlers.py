from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject, CommandStart
import app.keyboards as kb
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.group import Group
from models.home_work import Homework
from app.utils import get_current_user
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
rt = Router()


@rt.callback_query(F.data.startswith('details_'))
async def get_details_homework(callback: CallbackQuery, session: AsyncSession):
    homework_id = int(callback.data.split('_')[1])
    homework = (await session.execute(select(Homework).where(Homework.id == homework_id))).scalar_one_or_none()
    if homework.format_message == 'text':
        await callback.message.answer(f'Домашнее задание:\n{homework.data}')
    elif homework.format_message == 'pdf':
        await callback.message.answer_document(homework.data)
    await callback.answer()


@rt.message(Command('s_send_homework'))
async def send_homework(message: Message, session: AsyncSession):
    current_user = await get_current_user(session, message.from_user.id)
    if current_user.is_teacher or current_user.is_admin:
        await message.answer(f'Выберите группу в которую хотите отправить домашнее задание',
                             reply_markup=await kb.student_group_builder(session, message.from_user.id))


class HomeWorkForm(StatesGroup):
    waiting_for_answer = State()


@rt.callback_query(F.data.startswith('sgroup_'))
async def group_handler(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    group_name = callback.data.split('_')[1]
    print(group_name)
    await state.update_data(group=group_name)
    await state.set_state(HomeWorkForm.waiting_for_answer)
    await callback.message.edit_text(f'Вы выбрали группу {group_name}. Отправьте фото или напишите текстом вашу домашнюю работу.')


@rt.message(HomeWorkForm.waiting_for_answer)
async def send_homework(message: Message, session: AsyncSession):
    if message.photo:
        ...
