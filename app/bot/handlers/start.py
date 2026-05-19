from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.keyboards.main_menu import get_main_menu
from app.services.user_service import UserService
from app.config import settings

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession):
    if message.from_user is None:
        return

    user_service = UserService(session)
    user = await user_service.get_or_create_user(message.from_user)

    await message.answer(
        text = (
            f"🎵 <b>Добро пожаловать в бота лейбла <a href='{settings.label_link}'>{settings.label_name}</a>!</b>\n\n"
            f"Здесь ты сможешь отправить релиз, связать YouTube канал с Topic, "
            f"мониторить свой профиль и баланс, посмотреть FAQ лейбла и многое другое."
        ),
        reply_markup=get_main_menu(user.role),
    )
