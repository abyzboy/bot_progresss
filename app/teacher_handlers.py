from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject, CommandStart
import app.keyboards as kb
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.group import Group
from app.utils import get_current_user, save_homework, broadcast_homework_notification
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
rt = Router()


@rt.message(Command('create_group'))
async def create_group(message: Message, command: CommandObject, session: AsyncSession):
    # Получаем текущего пользователя
    current_user = await get_current_user(session, message.from_user.id)

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


class HomeWorkForm(StatesGroup):
    waiting_for_theme = State()
    waiting_for_date = State()
    waiting_for_content = State()


@rt.message(Command('t_send_homework'))
async def send_homework(message: Message, session: AsyncSession):
    current_user = await get_current_user(session, message.from_user.id)
    if current_user.is_teacher or current_user.is_admin:
        await message.answer(f'Выберите группу, которой хотите задать домашнее задание',
                             reply_markup=await kb.own_group_builder(session, message.from_user.id))
    else:
        await message.answer(f'У вас недостаточно прав, что бы задавать домашнее задание.')


@rt.callback_query(F.data.startswith('owngroup_'))
async def group_handler(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    group_name = callback.data.split('_')[1]
    print(group_name)
    await state.update_data(group=group_name)
    await state.set_state(HomeWorkForm.waiting_for_theme)
    await callback.message.edit_text(f'Вы выбрали группу {group_name}. Напишите на какую тему/урок будет домашнее задание.')


@rt.message(HomeWorkForm.waiting_for_theme)
async def process_theme(message: Message, state: FSMContext):
    theme = message.text
    await state.update_data(theme=theme)
    await state.set_state(HomeWorkForm.waiting_for_content)
    await message.answer('Напишите сообщением домашние задание или отправьте pdf файл')


@rt.message(HomeWorkForm.waiting_for_content)
async def process_content(message: Message, state: FSMContext):
    if message.content_type == types.ContentType.TEXT:
        print(message.text)
        await state.update_data(format_message='text', msg=message.text)
        await state.set_state(HomeWorkForm.waiting_for_date)
        await message.answer("✅ Текстовое задание сохранено! Напишите на какую дату хотите задать домашнее задание.\nФормат ввода 23.04")
    elif (message.document and
          message.document.mime_type == 'application/pdf'):
        await state.update_data(format_message='pdf', msg=message.document.file_id)
        await state.set_state(HomeWorkForm.waiting_for_date)
        await message.answer("✅ Pdf файл сохранен. Напишите на какую дату хотите задать домашнее задание.\nФормат ввода: ДЕНЬ.МЕСЯЦ")


@rt.message(HomeWorkForm.waiting_for_date)
async def homework_date(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    user_data = await state.get_data()
    format_message = user_data['format_message']
    theme = user_data['theme']
    data = user_data['msg']
    date = message.text
    group_name = user_data['group']
    group = (await session.execute(select(Group).where(Group.name == group_name))).scalar_one_or_none()
    homework = await save_homework(teacher_id=message.from_user.id, format_message=format_message,
                                   data=data, date=date, session=session, group=group, theme=theme)
    await broadcast_homework_notification(bot, session, f'Домашнее задание на тему {theme} от {group_name}', group, homework_id=homework.id)
    await message.answer('Ваше домашнее задание было успешно отправлено.')
