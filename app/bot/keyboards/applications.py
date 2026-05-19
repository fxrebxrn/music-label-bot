from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.db.models import Application

def my_applications_keyboard(
    applications: list[Application],
) -> InlineKeyboardMarkup:
    buttons = []

    for application in applications:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Открыть заявку #{application.id}",
                    callback_data=f"my_applications:open:{application.id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def application_details_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к списку",
                    callback_data="my_applications:back",
                )
            ]
        ]
    )
