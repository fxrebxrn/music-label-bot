from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from app.db.enums import UserRole

def get_main_menu(role: UserRole) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Профиль"), KeyboardButton(text="Мои заявки")],
        [KeyboardButton(text="Отправить релиз"), KeyboardButton(text="Связать YouTube канал")],
        [KeyboardButton(text="FAQ")],
        []
    ]

    if role in (UserRole.MODERATOR, UserRole.ADMIN):
        buttons[3].append(KeyboardButton(text="Модерация"))
        if role == UserRole.ADMIN:
            buttons[3].append(KeyboardButton(text="Админ-панель"))

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )
