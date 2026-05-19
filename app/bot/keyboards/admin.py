from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.db.models import Application

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin:stats",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔎 Найти заявку по ID",
                    callback_data="admin:search_application",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛡 Выдать роль",
                    callback_data="admin:give_role",
                )
            ],
        ]
    )

def admin_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад в админ-панель",
                    callback_data="admin:back",
                )
            ]
        ]
    )

def admin_archive_keyboard(
    applications: list[Application],
) -> InlineKeyboardMarkup:
    buttons = []

    for application in applications:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Открыть заявку #{application.id}",
                    callback_data=f"admin:open_application:{application.id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад в админ-панель",
                callback_data="admin:back",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_application_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к архиву",
                    callback_data="admin:applications_archive",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Админ-панель",
                    callback_data="admin:back",
                )
            ],
        ]
    )

def choose_role_keyboard(username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛡 Moderator",
                    callback_data=f"admin:set_role:{username}:moderator",
                )
            ],
            [
                InlineKeyboardButton(
                    text="👑 Admin",
                    callback_data=f"admin:set_role:{username}:admin",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎵 Artist",
                    callback_data=f"admin:set_role:{username}:artist",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад в админ-панель",
                    callback_data="admin:back",
                )
            ],
        ]
    )
