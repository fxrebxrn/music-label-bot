from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def account_link_terms_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Начать",
                    callback_data="account_link:start",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="account_link:cancel",
                )
            ],
        ]
    )

def account_link_step_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="account_link:back",
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="account_link:cancel",
                ),
            ]
        ]
    )

def account_link_preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📨 Отправить заявку",
                    callback_data="account_link:submit",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="account_link:back",
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="account_link:cancel",
                ),
            ],
        ]
    )
