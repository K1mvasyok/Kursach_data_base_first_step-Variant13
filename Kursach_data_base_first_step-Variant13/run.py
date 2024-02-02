import asyncio
from aiogram import Bot, Dispatcher
from config import Token, ADMIN_TELEGRAM_ID
from app import handlers, admin
from app.database.models import async_main
from aiogram.fsm.storage.memory import MemoryStorage


async def on_shutdown(dp):
    await dp.storage.close()
    await dp.storage.wait_closed()


async def main():
    await async_main()
    bot = Bot(token=Token, parse_mode='HTML')
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers.router_u)
    dp.include_router(admin.router_a)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Выход')
