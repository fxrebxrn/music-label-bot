import asyncio
from app.bot.loader import bot, dp
from app.bot.middlewares.db import DBSessionMiddleware
from app.db.database import async_session_maker
from app.bot.handlers.start import router as start_router
from app.bot.handlers.profile import router as profile_router
from app.bot.handlers.account_link import router as account_link_router
from app.bot.handlers.release import router as release_router
from app.bot.handlers.applications import router as applications_router
from app.bot.handlers.moderation import router as moderation_router
from app.bot.handlers.faq import router as faq_router
from app.bot.handlers.admin import router as admin_router

async def main():
    dp.update.middleware(DBSessionMiddleware(async_session_maker))

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(account_link_router)
    dp.include_router(release_router)
    dp.include_router(applications_router)
    dp.include_router(moderation_router)
    dp.include_router(faq_router)
    dp.include_router(admin_router)

    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен!")
