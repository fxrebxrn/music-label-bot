from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def faq_keyboard(items: dict) -> InlineKeyboardMarkup:
    buttons = []

    for item in items.values():
        buttons.append(
            [
                InlineKeyboardButton(
                    text=item["title"],
                    url=item["url"],
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
