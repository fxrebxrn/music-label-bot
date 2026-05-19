from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.release import (
    release_artist_type_keyboard,
    release_distribution_keyboard,
    release_explicit_keyboard,
    release_format_keyboard,
    release_preview_keyboard,
    release_step_keyboard,
)
from app.bot.states.release import ReleaseStates
from app.db.enums import ReleaseFormat
from app.services.release_service import ReleaseService
from app.services.user_service import UserService
from app.utils.release_formatting import build_release_preview

router = Router()


FIRST_STEPS_TOTAL = 12
SINGLE_TOTAL_STEPS = 11
MULTI_TOTAL_STEPS = 12


def is_single(data: dict) -> bool:
    return data.get("release_format") == ReleaseFormat.SINGLE.value


def total_steps(data: dict) -> int:
    return SINGLE_TOTAL_STEPS if is_single(data) else MULTI_TOTAL_STEPS


def step_text(step: int, total: int, title: str, description: str) -> str:
    return f"{title} <b>Шаг {step}/{total}</b>\n\n{description}"


def main_artists_text(data: dict) -> str:
    return step_text(
        4,
        total_steps(data),
        "👥",
        (
            "Введите основного артиста или артистов.\n\n"
            "Это тот артист/авторы, под кем выходит релиз.\n"
            "Если их несколько — можно через запятую или с новой строки."
        ),
    )


def release_title_text(data: dict) -> str:
    if is_single(data):
        description = "Введите название трека."
    else:
        description = "Введите название релиза."

    return step_text(5, total_steps(data), "🎵", description)


def tracks_order_text(data: dict) -> str:
    return step_text(
        6,
        total_steps(data),
        "📃",
        (
            "Перечислите треки в нужном порядке.\n\n"
            "Пример:\n"
            "Intro\n"
            "Night Drive\n"
            "Outro"
        ),
    )


def explicit_text(data: dict) -> str:
    step = 6 if is_single(data) else 7
    return step_text(
        step,
        total_steps(data),
        "🔞",
        "Есть ли в релизе ненормативная лексика?",
    )


def release_date_text(data: dict) -> str:
    step = 7 if is_single(data) else 8
    return step_text(
        step,
        total_steps(data),
        "📅",
        (
            "Введите дату релиза в формате <b>ДД.ММ.ГГГГ</b>.\n\n"
            "Пример: <code>25.06.2026</code>"
        ),
    )


def genre_text(data: dict) -> str:
    step = 8 if is_single(data) else 9
    return step_text(step, total_steps(data), "🎼", "Введите жанр релиза.")


def materials_text(data: dict) -> str:
    step = 9 if is_single(data) else 10
    return step_text(
        step,
        total_steps(data),
        "📎",
        (
            "Отправьте ссылку на материалы релиза.\n\n"
            "Например: Google Drive, Dropbox, OneDrive."
        ),
    )


def artist_full_name_text(data: dict) -> str:
    step = 10 if is_single(data) else 11
    return step_text(
        step,
        total_steps(data),
        "🪪",
        "Введите имя и фамилию артиста.",
    )


def comment_text(data: dict) -> str:
    step = 11 if is_single(data) else 12
    return step_text(
        step,
        total_steps(data),
        "💬",
        "Введите комментарий к релизу или отправьте <code>-</code>, если комментария нет.",
    )


@router.message(F.text == "Отправить релиз")
async def release_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ReleaseStates.distribution_type)

    await message.answer(
        text=step_text(
            1,
            FIRST_STEPS_TOTAL,
            "🎵",
            "Какая будет дистрибуция?",
        ),
        reply_markup=release_distribution_keyboard(),
    )


@router.callback_query(
    ReleaseStates.distribution_type,
    F.data.startswith("release:distribution:"),
)
async def process_distribution_type(callback: CallbackQuery, state: FSMContext):
    distribution_type = callback.data.split(":")[-1]

    await state.update_data(distribution_type=distribution_type)
    await state.set_state(ReleaseStates.artist_type)

    if callback.message:
        await callback.message.edit_text(
            text=step_text(
                2,
                FIRST_STEPS_TOTAL,
                "🎧",
                "Кем вы являетесь?",
            ),
            reply_markup=release_artist_type_keyboard(),
        )

    await callback.answer()


@router.callback_query(
    ReleaseStates.artist_type,
    F.data.startswith("release:artist_type:"),
)
async def process_artist_type(callback: CallbackQuery, state: FSMContext):
    artist_type = callback.data.split(":")[-1]

    await state.update_data(artist_type=artist_type)
    await state.set_state(ReleaseStates.release_format)

    if callback.message:
        await callback.message.edit_text(
            text=step_text(
                3,
                FIRST_STEPS_TOTAL,
                "📦",
                "Выберите формат релиза.",
            ),
            reply_markup=release_format_keyboard(),
        )

    await callback.answer()


@router.callback_query(
    ReleaseStates.release_format,
    F.data.startswith("release:format:"),
)
async def process_release_format(callback: CallbackQuery, state: FSMContext):
    release_format = callback.data.split(":")[-1]

    await state.update_data(release_format=release_format)
    await state.set_state(ReleaseStates.main_artists)

    data = await state.get_data()

    if callback.message:
        await callback.message.edit_text(
            text=main_artists_text(data),
            reply_markup=release_step_keyboard(),
        )

    await callback.answer()


@router.message(ReleaseStates.main_artists)
async def process_main_artists(message: Message, state: FSMContext):
    await state.update_data(main_artists=message.text)
    await state.set_state(ReleaseStates.release_title)

    data = await state.get_data()

    await message.answer(
        text=release_title_text(data),
        reply_markup=release_step_keyboard(),
    )


@router.message(ReleaseStates.release_title)
async def process_release_title(message: Message, state: FSMContext):
    data = await state.get_data()

    if is_single(data):
        await state.update_data(
            release_title=message.text,
            single_track_title=message.text,
        )
        await ask_explicit_content(message, state)
        return

    await state.update_data(release_title=message.text)
    await state.set_state(ReleaseStates.tracks_order)

    data = await state.get_data()

    await message.answer(
        text=tracks_order_text(data),
        reply_markup=release_step_keyboard(),
    )


@router.message(ReleaseStates.tracks_order)
async def process_tracks_order(message: Message, state: FSMContext):
    await state.update_data(tracks_order=message.text)
    await ask_explicit_content(message, state)


async def ask_explicit_content(message: Message, state: FSMContext):
    await state.set_state(ReleaseStates.explicit_content)
    data = await state.get_data()

    await message.answer(
        text=explicit_text(data),
        reply_markup=release_explicit_keyboard(),
    )


@router.callback_query(
    ReleaseStates.explicit_content,
    F.data.startswith("release:explicit:"),
)
async def process_explicit_content(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split(":")[-1]
    has_explicit_content = answer == "yes"

    await state.update_data(has_explicit_content=has_explicit_content)
    await state.set_state(ReleaseStates.release_date)

    data = await state.get_data()

    if callback.message:
        await callback.message.edit_text(
            text=release_date_text(data),
            reply_markup=release_step_keyboard(),
        )

    await callback.answer()


@router.message(ReleaseStates.release_date)
async def process_release_date(message: Message, state: FSMContext):
    if not message.text:
        return

    data = await state.get_data()

    try:
        datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        await message.answer(
            text=(
                "❌ Неверный формат даты.\n\n"
                "Введите дату в формате <b>ДД.ММ.ГГГГ</b>.\n"
                "Пример: <code>25.06.2026</code>"
            ),
            reply_markup=release_step_keyboard(),
        )
        return

    await state.update_data(release_date=message.text)
    await state.set_state(ReleaseStates.genre)

    data = await state.get_data()

    await message.answer(
        text=genre_text(data),
        reply_markup=release_step_keyboard(),
    )


@router.message(ReleaseStates.genre)
async def process_genre(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await state.set_state(ReleaseStates.materials_link)

    data = await state.get_data()

    await message.answer(
        text=materials_text(data),
        reply_markup=release_step_keyboard(),
    )


@router.message(ReleaseStates.materials_link)
async def process_materials_link(message: Message, state: FSMContext):
    await state.update_data(materials_link=message.text)
    await state.set_state(ReleaseStates.artist_full_name)

    data = await state.get_data()

    await message.answer(
        text=artist_full_name_text(data),
        reply_markup=release_step_keyboard(),
    )


@router.message(ReleaseStates.artist_full_name)
async def process_artist_full_name(message: Message, state: FSMContext):
    await state.update_data(artist_full_name=message.text)
    await state.set_state(ReleaseStates.comment)

    data = await state.get_data()

    await message.answer(
        text=comment_text(data),
        reply_markup=release_step_keyboard(),
    )


@router.message(ReleaseStates.comment)
async def process_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)

    data = await state.get_data()
    preview_text = build_release_preview(data)

    await state.set_state(ReleaseStates.preview)

    await message.answer(
        text=preview_text,
        reply_markup=release_preview_keyboard(),
    )


@router.callback_query(ReleaseStates.preview, F.data == "release:submit")
async def submit_release_application(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()

    user_service = UserService(session)
    user = await user_service.get_or_create_user(callback.from_user)

    release_service = ReleaseService(session)
    application = await release_service.create_release_application(
        user=user,
        data=data,
    )

    await state.clear()

    if callback.message:
        await callback.message.edit_text(
            text=(
                "✅ <b>Заявка на релиз отправлена!</b>\n\n"
                f"Номер заявки: <b>#{application.id}</b>\n\n"
                "Заявка будет рассмотрена в течение <b>3-7 дней.</b>"
            )
        )

    await callback.answer()


@router.callback_query(F.data == "release:cancel")
async def cancel_release_form(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    if callback.message:
        await callback.message.edit_text(
            text="❌ Отправка релиза отменена."
        )

    await callback.answer()


@router.callback_query(F.data == "release:back")
async def back_release_form(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == ReleaseStates.artist_type.state:
        await state.set_state(ReleaseStates.distribution_type)
        text = step_text(1, FIRST_STEPS_TOTAL, "🎵", "Какая будет дистрибуция?")
        keyboard = release_distribution_keyboard()

    elif current_state == ReleaseStates.release_format.state:
        await state.set_state(ReleaseStates.artist_type)
        text = step_text(2, FIRST_STEPS_TOTAL, "🎧", "Кем вы являетесь?")
        keyboard = release_artist_type_keyboard()

    elif current_state == ReleaseStates.main_artists.state:
        await state.set_state(ReleaseStates.release_format)
        text = step_text(3, FIRST_STEPS_TOTAL, "📦", "Выберите формат релиза.")
        keyboard = release_format_keyboard()

    elif current_state == ReleaseStates.release_title.state:
        await state.set_state(ReleaseStates.main_artists)
        text = main_artists_text(data)
        keyboard = release_step_keyboard()

    elif current_state == ReleaseStates.tracks_order.state:
        await state.set_state(ReleaseStates.release_title)
        text = release_title_text(data)
        keyboard = release_step_keyboard()

    elif current_state == ReleaseStates.explicit_content.state:
        if is_single(data):
            await state.set_state(ReleaseStates.release_title)
            text = release_title_text(data)
        else:
            await state.set_state(ReleaseStates.tracks_order)
            text = tracks_order_text(data)

        keyboard = release_step_keyboard()

    elif current_state == ReleaseStates.release_date.state:
        await state.set_state(ReleaseStates.explicit_content)
        text = explicit_text(data)
        keyboard = release_explicit_keyboard()

    elif current_state == ReleaseStates.genre.state:
        await state.set_state(ReleaseStates.release_date)
        text = release_date_text(data)
        keyboard = release_step_keyboard()

    elif current_state == ReleaseStates.materials_link.state:
        await state.set_state(ReleaseStates.genre)
        text = genre_text(data)
        keyboard = release_step_keyboard()

    elif current_state == ReleaseStates.artist_full_name.state:
        await state.set_state(ReleaseStates.materials_link)
        text = materials_text(data)
        keyboard = release_step_keyboard()

    elif current_state == ReleaseStates.comment.state:
        await state.set_state(ReleaseStates.artist_full_name)
        text = artist_full_name_text(data)
        keyboard = release_step_keyboard()

    elif current_state == ReleaseStates.preview.state:
        await state.set_state(ReleaseStates.comment)
        text = comment_text(data)
        keyboard = release_step_keyboard()

    else:
        await callback.answer("Назад отсюда недоступен.", show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
        )

    await callback.answer()
