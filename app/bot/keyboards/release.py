from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def release_distribution_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Платная",
                    callback_data="release:distribution:paid",
                ),
                InlineKeyboardButton(
                    text="🆓 Бесплатная",
                    callback_data="release:distribution:free",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="release:cancel",
                )
            ],
        ]
    )

def release_artist_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎤 Исполнитель / Певец",
                    callback_data="release:artist_type:singer",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎛 Битмейкер / DJ / Продюсер",
                    callback_data="release:artist_type:producer",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="release:back",
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="release:cancel",
                ),
            ],
        ]
    )

def release_format_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎵 Сингл — 1 трек",
                    callback_data="release:format:single",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💿 EP",
                    callback_data="release:format:ep",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📀 Альбом",
                    callback_data="release:format:album",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="release:back",
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="release:cancel",
                ),
            ],
        ]
    )

def release_explicit_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да",
                    callback_data="release:explicit:yes",
                ),
                InlineKeyboardButton(
                    text="Нет",
                    callback_data="release:explicit:no",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="release:back",
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="release:cancel",
                ),
            ],
        ]
    )

def release_step_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="release:back",
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="release:cancel",
                ),
            ]
        ]
    )

def release_preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📨 Отправить заявку",
                    callback_data="release:submit",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="release:back",
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="release:cancel",
                ),
            ],
        ]
    )
