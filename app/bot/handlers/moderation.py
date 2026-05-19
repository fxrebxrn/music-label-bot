from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.keyboards.moderation import (
    moderation_back_keyboard,
    moderation_details_keyboard,
    moderation_queue_keyboard,
    moderation_comment_keyboard,
)
from app.services.moderation_service import ModerationService
from app.services.user_service import UserService
from app.bot.states.moderation import ModerationStates
from aiogram.fsm.context import FSMContext
from aiogram.types import User as TelegramUser
from app.bot.filters.role import RoleFilter
from app.db.models import User
from app.db.enums import UserRole

router = Router()
router.message.filter(RoleFilter(UserRole.MODERATOR, UserRole.ADMIN))
router.callback_query.filter(RoleFilter(UserRole.MODERATOR, UserRole.ADMIN))

async def finish_moderation_decision(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    moderator_telegram_user: TelegramUser,
    status: str,
    comment: str | None,
):
    data = await state.get_data()
    application_id = data.get("application_id")

    if not application_id:
        await message.answer("Ошибка: заявка не найдена в состоянии.")
        await state.clear()
        return

    user_service = UserService(session)
    moderator = await user_service.get_or_create_user(moderator_telegram_user)

    moderation_service = ModerationService(session)

    if not moderation_service.can_moderate(moderator):
        await message.answer("⛔ У вас нет доступа.")
        await state.clear()
        return

    application = await moderation_service.get_application_for_moderation(
        application_id=int(application_id),
    )

    if application is None:
        await message.answer("Заявка не найдена.")
        await state.clear()
        return

    if status == "approve":
        await moderation_service.approve_application(
            application=application,
            moderator=moderator,
            moderator_comment=comment,
        )
        result_text = "✅ принята"
    else:
        await moderation_service.reject_application(
            application=application,
            moderator=moderator,
            moderator_comment=comment,
        )
        result_text = "❌ отклонена"

    if application.user:
        notification_text = moderation_service.build_user_decision_notification(
            application=application,
            moderator=moderator,
        )

        try:
            await message.bot.send_message(
                chat_id=application.user.telegram_id,
                text=notification_text,
            )
        except Exception:
            pass

    await state.clear()

    await message.answer(
        text=(
            f"Готово. Заявка #{application.id} {result_text}.\n\n"
            "Пользователь получил уведомление, если не заблокировал бота."
        ),
        reply_markup=moderation_back_keyboard(),
    )

@router.message(F.text == "Модерация")
async def moderation_handler(
    message: Message,
    session: AsyncSession,
):
    moderation_service = ModerationService(session)

    applications = await moderation_service.get_pending_applications()
    text = moderation_service.build_queue_text(applications)

    if not applications:
        await message.answer(text)
        return

    await message.answer(
        text=text,
        reply_markup=moderation_queue_keyboard(applications),
    )

@router.callback_query(F.data.startswith("moderation:open:"))
async def open_moderation_application_handler(
    callback: CallbackQuery,
    session: AsyncSession,
):
    if callback.from_user is None:
        return

    application_id = int(callback.data.split(":")[-1])

    user_service = UserService(session)
    user = await user_service.get_or_create_user(callback.from_user)

    moderation_service = ModerationService(session)

    if not moderation_service.can_moderate(user):
        await callback.answer(
            text="У вас нет доступа.",
            show_alert=True,
        )
        return

    application = await moderation_service.get_application_for_moderation(
        application_id=application_id,
    )

    if application is None:
        await callback.answer(
            text="Заявка не найдена.",
            show_alert=True,
        )
        return

    text = moderation_service.build_application_text(application)

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=moderation_details_keyboard(application.id),
        )

    await callback.answer()

@router.callback_query(F.data == "moderation:back")
async def back_to_moderation_queue_handler(
    callback: CallbackQuery,
    session: AsyncSession,
):
    if callback.from_user is None:
        return

    user_service = UserService(session)
    user = await user_service.get_or_create_user(callback.from_user)

    moderation_service = ModerationService(session)

    if not moderation_service.can_moderate(user):
        await callback.answer(
            text="У вас нет доступа.",
            show_alert=True,
        )
        return

    applications = await moderation_service.get_pending_applications()
    text = moderation_service.build_queue_text(applications)

    if callback.message:
        if applications:
            await callback.message.edit_text(
                text=text,
                reply_markup=moderation_queue_keyboard(applications),
            )
        else:
            await callback.message.edit_text(text=text)

    await callback.answer()

@router.callback_query(F.data.startswith("moderation:approve:"))
async def approve_application_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    if callback.from_user is None:
        return

    application_id = int(callback.data.split(":")[-1])

    user_service = UserService(session)
    moderator = await user_service.get_or_create_user(callback.from_user)

    moderation_service = ModerationService(session)

    if not moderation_service.can_moderate(moderator):
        await callback.answer(
            text="У вас нет доступа.",
            show_alert=True,
        )
        return

    await state.update_data(application_id=application_id)
    await state.set_state(ModerationStates.approve_comment)

    if callback.message:
        await callback.message.edit_text(
            text=(
                f"✅ <b>Принятие заявки #{application_id}</b>\n\n"
                "Напишите комментарий для пользователя.\n\n"
                "Например:\n"
                "<code>Заявка принята, всё заполнено корректно.</code>"
            ),
            reply_markup=moderation_comment_keyboard(application_id),
        )

    await callback.answer()

@router.callback_query(F.data.startswith("moderation:reject:"))
async def reject_application_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    if callback.from_user is None:
        return

    application_id = int(callback.data.split(":")[-1])

    user_service = UserService(session)
    moderator = await user_service.get_or_create_user(callback.from_user)

    moderation_service = ModerationService(session)

    if not moderation_service.can_moderate(moderator):
        await callback.answer(
            text="У вас нет доступа.",
            show_alert=True,
        )
        return

    await state.update_data(application_id=application_id)
    await state.set_state(ModerationStates.reject_comment)

    if callback.message:
        await callback.message.edit_text(
            text=(
                f"❌ <b>Отклонение заявки #{application_id}</b>\n\n"
                "Напишите причину отклонения для пользователя.\n\n"
                "Например:\n"
                "<code>Не хватает ссылок на материалы.</code>"
            ),
            reply_markup=moderation_comment_keyboard(application_id),
        )

    await callback.answer()

@router.message(ModerationStates.approve_comment)
async def process_approve_comment(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    if message.from_user is None:
        return

    await finish_moderation_decision(
        message=message,
        state=state,
        session=session,
        moderator_telegram_user=message.from_user,
        status="approve",
        comment=message.text,
    )


@router.message(ModerationStates.reject_comment)
async def process_reject_comment(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    if message.from_user is None:
        return

    await finish_moderation_decision(
        message=message,
        state=state,
        session=session,
        moderator_telegram_user=message.from_user,
        status="reject",
        comment=message.text,
    )

@router.callback_query(F.data == "moderation:no_comment")
async def no_comment_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    current_state = await state.get_state()

    if current_state == ModerationStates.approve_comment.state:
        status = "approve"
    elif current_state == ModerationStates.reject_comment.state:
        status = "reject"
    else:
        await callback.answer()
        return

    if callback.message:
        await finish_moderation_decision(
            message=callback.message,
            state=state,
            session=session,
            moderator_telegram_user=callback.from_user,
            status=status,
            comment=None,
        )

    await callback.answer()

@router.callback_query(F.data.startswith("moderation:back_to_application:"))
async def back_to_application_from_comment_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    if callback.from_user is None:
        return

    application_id = int(callback.data.split(":")[-1])

    user_service = UserService(session)
    moderator = await user_service.get_or_create_user(callback.from_user)

    moderation_service = ModerationService(session)

    if not moderation_service.can_moderate(moderator):
        await callback.answer(
            text="У вас нет доступа.",
            show_alert=True,
        )
        return

    application = await moderation_service.get_application_for_moderation(
        application_id=application_id,
    )

    if application is None:
        await callback.answer(
            text="Заявка не найдена.",
            show_alert=True,
        )
        return

    await state.clear()

    text = moderation_service.build_application_text(application)

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=moderation_details_keyboard(application.id),
        )

    await callback.answer()
