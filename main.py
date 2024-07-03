import asyncio
from settings import dp, bot
from handlers.user import user_router
from handlers.admin import admin_router
from services import database


# Запуск процесса поллинга новых апдейтов
async def main():
    database.init_db()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # запуск бота
    asyncio.run(main())
