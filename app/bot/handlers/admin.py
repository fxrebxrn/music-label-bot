from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.keyboards.admin import (
    admin_application_keyboard,
    admin_archive_keyboard,
    admin_back_keyboard,
    admin_panel_keyboard,
    choose_role_keyboard,
)
from app.bot.states.admin import AdminStates
from app.db.enums import UserRole
from app.services.admin_service import AdminService
from app.services.user_service import UserService
from app.bot.filters.role import RoleFilter
from app.db.models import User

router = Router()
router.message.filter(RoleFilter(UserRole.ADMIN))
router.callback_query.filter(RoleFilter(UserRole.ADMIN))

@router.message(F.text == "Админ-панель")
async def admin_panel_handler(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    current_user: User,
):
    await state.clear()

    admin_service = AdminService(session)

    await message.answer(
        text=admin_service.build_admin_panel_text(current_user),
        reply_markup=admin_panel_keyboard(),
    )

@router.callback_query(F.data == "admin:back")
async def back_to_admin_panel_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    await state.clear()

    user_service = UserService(session)
    admin = await user_service.get_or_create_user(callback.from_user)

    admin_service = AdminService(session)

    if not admin_service.can_admin(admin):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            text=admin_service.build_admin_panel_text(admin),
            reply_markup=admin_panel_keyboard(),
        )

    await callback.answer()

@router.callback_query(F.data == "admin:stats")
async def admin_stats_handler(
    callback: CallbackQuery,
    session: AsyncSession,
):
    admin_service = AdminService(session)

    text = await admin_service.get_stats_text()

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=admin_back_keyboard(),
        )

    await callback.answer()

@router.callback_query(F.data == "admin:applications_archive")
async def admin_applications_archive_handler(
    callback: CallbackQuery,
    session: AsyncSession,
):
    user_service = UserService(session)
    admin = await user_service.get_or_create_user(callback.from_user)

    admin_service = AdminService(session)

    if not admin_service.can_admin(admin):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    applications = await admin_service.get_archive()
    text = admin_service.build_archive_text(applications)

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=admin_archive_keyboard(applications),
        )

    await callback.answer()

@router.callback_query(F.data.startswith("admin:open_application:"))
async def admin_open_application_handler(
    callback: CallbackQuery,
    session: AsyncSession,
):
    user_service = UserService(session)
    admin = await user_service.get_or_create_user(callback.from_user)

    admin_service = AdminService(session)

    if not admin_service.can_admin(admin):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    application_id = int(callback.data.split(":")[-1])
    application = await admin_service.get_application_by_id(application_id)

    if application is None:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    text = admin_service.build_application_text(application)

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=admin_application_keyboard(),
        )

    await callback.answer()

@router.callback_query(F.data == "admin:search_application")
async def admin_search_application_start_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    user_service = UserService(session)
    admin = await user_service.get_or_create_user(callback.from_user)

    admin_service = AdminService(session)

    if not admin_service.can_admin(admin):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await state.set_state(AdminStates.search_application_id)

    if callback.message:
        await callback.message.edit_text(
            text=(
                "🔎 <b>Поиск заявки по ID</b>\n\n"
                "Введите ID заявки числом.\n\n"
                "Например: <code>15</code>"
            ),
            reply_markup=admin_back_keyboard(),
        )

    await callback.answer()

@router.message(AdminStates.search_application_id)
async def admin_search_application_process_handler(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    if message.from_user is None:
        return

    user_service = UserService(session)
    admin = await user_service.get_or_create_user(message.from_user)

    admin_service = AdminService(session)

    if not admin_service.can_admin(admin):
        await message.answer("⛔ У вас нет доступа.")
        await state.clear()
        return

    if not message.text or not message.text.isdigit():
        await message.answer(
            "❌ Введите ID заявки числом.\n\n"
            "Например: <code>15</code>"
        )
        return

    application = await admin_service.get_application_by_id(
        application_id=int(message.text),
    )

    await state.clear()

    if application is None:
        await message.answer(
            text="❌ Заявка с таким ID не найдена.",
            reply_markup=admin_back_keyboard(),
        )
        return

    await message.answer(
        text=admin_service.build_application_text(application),
        reply_markup=admin_application_keyboard(),
    )

@router.callback_query(F.data == "admin:give_role")
async def admin_give_role_start_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    user_service = UserService(session)
    admin = await user_service.get_or_create_user(callback.from_user)

    admin_service = AdminService(session)

    if not admin_service.can_admin(admin):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await state.set_state(AdminStates.enter_username_for_role)

    if callback.message:
        await callback.message.edit_text(
            text=(
                "🛡 <b>Выдача роли</b>\n\n"
                "Введите username пользователя.\n\n"
                "Можно с @ или без.\n\n"
                "Например:\n"
                "<code>@username</code>"
            ),
            reply_markup=admin_back_keyboard(),
        )

    await callback.answer()

@router.message(AdminStates.enter_username_for_role)
async def admin_enter_username_for_role_handler(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    if message.from_user is None:
        return

    user_service = UserService(session)
    admin = await user_service.get_or_create_user(message.from_user)

    admin_service = AdminService(session)

    if not admin_service.can_admin(admin):
        await message.answer("⛔ У вас нет доступа.")
        await state.clear()
        return

    if not message.text:
        await message.answer("❌ Введите username.")
        return

    username = message.text.strip().removeprefix("@")

    user = await admin_service.get_user_by_username(username)

    if user is None:
        await message.answer(
            "❌ Пользователь не найден.\n\n"
            "Важно: пользователь должен хотя бы один раз запустить бота через /start."
        )
        return

    await state.update_data(username=username)
    await state.set_state(AdminStates.choose_role)

    await message.answer(
        text=admin_service.build_found_user_text(user),
        reply_markup=choose_role_keyboard(username),
    )

@router.callback_query(
    AdminStates.choose_role,
    F.data.startswith("admin:set_role:"),
)
async def admin_set_role_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    user_service = UserService(session)
    admin = await user_service.get_or_create_user(callback.from_user)

    admin_service = AdminService(session)

    if not admin_service.can_admin(admin):
        await callback.answer("Нет доступа.", show_alert=True)
        await state.clear()
        return

    _, _, username, role_value = callback.data.split(":")

    user = await admin_service.get_user_by_username(username)

    if user is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        await state.clear()
        return

    new_role = UserRole(role_value)

    await admin_service.set_user_role(
        user=user,
        role=new_role,
    )

    await state.clear()

    if callback.message:
        await callback.message.edit_text(
            text=admin_service.build_role_changed_text(user),
            reply_markup=admin_back_keyboard(),
        )

    await callback.answer("Роль обновлена.")
