from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.keyboards.applications import (
    application_details_keyboard,
    my_applications_keyboard,
)
from app.services.application_service import ApplicationService
from app.services.user_service import UserService

router = Router()

@router.message(F.text == "Мои заявки")
async def my_applications_handler(
    message: Message,
    session: AsyncSession,
):
    if message.from_user is None:
        return

    user_service = UserService(session)
    user = await user_service.get_or_create_user(message.from_user)

    applications_service = ApplicationService(session)
    applications = await applications_service.get_user_applications(user)

    text = applications_service.build_applications_list_text(applications)

    if not applications:
        await message.answer(text)
        return

    await message.answer(
        text=text,
        reply_markup=my_applications_keyboard(applications),
    )

@router.callback_query(F.data.startswith("my_applications:open:"))
async def open_my_application_handler(
    callback: CallbackQuery,
    session: AsyncSession,
):
    if callback.from_user is None:
        return

    application_id = int(callback.data.split(":")[-1])

    user_service = UserService(session)
    user = await user_service.get_or_create_user(callback.from_user)

    applications_service = ApplicationService(session)
    application = await applications_service.get_user_application_by_id(
        user=user,
        application_id=application_id,
    )

    if application is None:
        await callback.answer(
            text="Заявка не найдена.",
            show_alert=True,
        )
        return

    text = applications_service.build_application_details_text(application)

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=application_details_keyboard(),
        )

    await callback.answer()

@router.callback_query(F.data == "my_applications:back")
async def back_to_my_applications_handler(
    callback: CallbackQuery,
    session: AsyncSession,
):
    if callback.from_user is None:
        return

    user_service = UserService(session)
    user = await user_service.get_or_create_user(callback.from_user)

    applications_service = ApplicationService(session)
    applications = await applications_service.get_user_applications(user)

    text = applications_service.build_applications_list_text(applications)

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=my_applications_keyboard(applications),
        )

    await callback.answer()
