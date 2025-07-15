from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Отправить домашнее задание.'),
               KeyboardButton(text='Присоединиться в группу.')],
              [KeyboardButton(text='Все мои группы')]],
    resize_keyboard=True)
