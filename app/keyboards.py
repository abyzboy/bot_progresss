from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .utils import get_groups, get_own_groups, get_student_groups
from sqlalchemy.ext.asyncio import AsyncSession
main = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Отправить домашнее задание.'),
               KeyboardButton(text='Присоединиться в группу.')],
              [KeyboardButton(text='Все мои группы')]],
    resize_keyboard=True)


async def student_group_builder(session: AsyncSession, user_id):
    groups = await get_student_groups(session, user_id)
    keyboard = InlineKeyboardBuilder()
    for group in groups:
        keyboard.add(InlineKeyboardButton(
            text=group.name, callback_data=f'sgroup_{group.name}'))
    return keyboard.adjust(2).as_markup()


async def group_builder(session: AsyncSession):
    groups = await get_groups(session)
    keyboard = InlineKeyboardBuilder()
    for group in groups:
        keyboard.add(InlineKeyboardButton(
            text=group.name, callback_data=f'group_{group.name}'))
    return keyboard.adjust(2).as_markup()


async def own_group_builder(session: AsyncSession, user_id):
    groups = await get_own_groups(session, user_id)
    keyboard = InlineKeyboardBuilder()
    for group in groups:
        keyboard.add(InlineKeyboardButton(
            text=group.name, callback_data=f'owngroup_{group.name}'))
    return keyboard.adjust(2).as_markup()
