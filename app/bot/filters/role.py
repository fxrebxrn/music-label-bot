from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.enums import UserRole
from app.services.user_service import UserService


class RoleFilter(Filter):
    def __init__(self, *roles: UserRole):
        self.roles = roles

    async def __call__(
        self,
        event: TelegramObject,
        session: AsyncSession,
    ) -> bool | dict:
        telegram_user = None

        if isinstance(event, Message):
            telegram_user = event.from_user

        elif isinstance(event, CallbackQuery):
            telegram_user = event.from_user

        if telegram_user is None:
            return False

        user_service = UserService(session)
        user = await user_service.get_or_create_user(telegram_user)

        if user.role not in self.roles:
            await self._send_no_access_message(event)
            return False

        return {
            "current_user": user,
        }

    async def _send_no_access_message(
        self,
        event: TelegramObject,
    ) -> None:
        if isinstance(event, CallbackQuery):
            await event.answer(
                text="У вас нет доступа.",
                show_alert=True,
            )
