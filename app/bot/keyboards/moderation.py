from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.db.models import Application

def moderation_queue_keyboard(
    applications: list[Application],
) -> InlineKeyboardMarkup:
    buttons = []

    for application in applications:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Открыть заявку #{application.id}",
                    callback_data=f"moderation:open:{application.id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def moderation_details_keyboard(application_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=f"moderation:approve:{application_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"moderation:reject:{application_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к очереди",
                    callback_data="moderation:back",
                )
            ],
        ]
    )

def moderation_comment_keyboard(application_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Без комментария",
                    callback_data="moderation:no_comment",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к заявке",
                    callback_data=f"moderation:back_to_application:{application_id}",
                )
            ],
        ]
    )

def moderation_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к очереди",
                    callback_data="moderation:back",
                )
            ]
        ]
    )
