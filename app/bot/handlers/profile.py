from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.profile_service import ProfileService
from app.services.user_service import UserService

router = Router()

@router.message(F.text == "Профиль")
async def profile_handler(message: Message, session: AsyncSession):
    if message.from_user is None:
        return

    user_service = UserService(session)
    user = await user_service.get_or_create_user(message.from_user)

    profile_service = ProfileService(session)
    profile_text = await profile_service.get_profile_text(user)

    await message.answer(profile_text)