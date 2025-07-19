import asyncio
from app.handlers import rt as handler_rt
from app.teacher_handlers import rt as teacher_rt
from app.student_handlers import rt as student_rt
from bot import bot, dp
import os
from database import Base, engine
from models.user import User
from models.group import Group
from models.user_group import UserGroup
from models.home_work import Homework


async def main():
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_router(handler_rt)
    dp.include_router(teacher_rt)
    dp.include_router(student_rt)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await dp.start_polling(bot)


async def startup(dispatcher):
    print('Starting up....')


async def shutdown(dispatcher):
    print('Shutting down...')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
