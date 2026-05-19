from aiogram.types import User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repository = UserRepository(session)

    async def get_or_create_user(self, telegram_user: TelegramUser) -> User:
        user = await self.user_repository.get_by_telegram_id(telegram_id=telegram_user.id)

        if user:
            return await self.user_repository.update_basic_info(
                user=user,
                username=telegram_user.username,
                full_name=telegram_user.full_name,
            )

        return await self.user_repository.create(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            full_name=telegram_user.full_name,
        )
