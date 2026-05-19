from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.keyboards.account_link import (
    account_link_preview_keyboard,
    account_link_step_keyboard,
    account_link_terms_keyboard,
)
from app.bot.states.account_link import AccountLinkStates
from app.services.application_service import ApplicationService
from app.services.user_service import UserService

router = Router()

ACCOUNT_LINK_TERMS_TEXT = (
    "🔗 <b>Связать канал с topic</b>\n\n"
    "<b>Перед отправкой заявки проверьте условия:</b>\n\n"
    "• На канале не должно быть нарушений.\n"
    "• На канале должно быть оформление: аватарка и шапка.\n"
    "• Канал должен быть не пустой, а активный.\n"
    "• Регулярно выходят ролики, в том числе с вашими релизами.\n"
    "• На topic и на основном канале должно быть минимум 3 одинаковых трека.\n\n"
    "Если всё подходит — нажмите <b>Начать</b>."
)

@router.message(F.text == "Связать YouTube канал")
async def account_link_terms_handler(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text=ACCOUNT_LINK_TERMS_TEXT,
        reply_markup=account_link_terms_keyboard(),
    )

@router.callback_query(F.data == "account_link:start")
async def start_account_link_form(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(AccountLinkStates.artist_nickname)

    if callback.message:
        await callback.message.edit_text(
            text=(
                "🎤 <b>Шаг 1/5</b>\n\n"
                "Введите никнейм артиста."
            ),
            reply_markup=account_link_step_keyboard(),
        )

    await callback.answer()

@router.message(AccountLinkStates.artist_nickname)
async def process_artist_nickname(message: Message, state: FSMContext):
    await state.update_data(artist_nickname=message.text)

    await state.set_state(AccountLinkStates.topic_channel_link)

    await message.answer(
        text=(
            "📺 <b>Шаг 2/5</b>\n\n"
            "Отправьте ссылку на topic-канал."
        ),
        reply_markup=account_link_step_keyboard(),
    )

@router.message(AccountLinkStates.topic_channel_link)
async def process_topic_channel_link(message: Message, state: FSMContext):
    await state.update_data(topic_channel_link=message.text)

    await state.set_state(AccountLinkStates.main_channel_link)

    await message.answer(
        text=(
            "📺 <b>Шаг 3/5</b>\n\n"
            "Отправьте ссылку на основной канал."
        ),
        reply_markup=account_link_step_keyboard(),
    )

@router.message(AccountLinkStates.main_channel_link)
async def process_main_channel_link(message: Message, state: FSMContext):
    await state.update_data(main_channel_link=message.text)

    await state.set_state(AccountLinkStates.topic_videos_links)

    await message.answer(
        text=(
            "🎬 <b>Шаг 4/5</b>\n\n"
            "Отправьте 3 ссылки на видео с topic-канала.\n\n"
            "Можно отправить каждую ссылку с новой строки."
        ),
        reply_markup=account_link_step_keyboard(),
    )

@router.message(AccountLinkStates.topic_videos_links)
async def process_topic_videos_links(message: Message, state: FSMContext):
    await state.update_data(topic_videos_links=message.text)

    await state.set_state(AccountLinkStates.main_videos_links)

    await message.answer(
        text=(
            "🎬 <b>Шаг 5/5</b>\n\n"
            "Отправьте 3 ссылки на видео с основного канала.\n\n"
            "Можно отправить каждую ссылку с новой строки."
        ),
        reply_markup=account_link_step_keyboard(),
    )

@router.message(AccountLinkStates.main_videos_links)
async def process_main_videos_links(message: Message, state: FSMContext):
    await state.update_data(main_videos_links=message.text)

    data = await state.get_data()
    preview_text = build_account_link_preview(data)

    await state.set_state(AccountLinkStates.preview)

    await message.answer(
        text=preview_text,
        reply_markup=account_link_preview_keyboard(),
    )

@router.callback_query(AccountLinkStates.preview, F.data == "account_link:submit")
async def submit_account_link_application(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    if callback.from_user is None:
        return

    data = await state.get_data()

    user_service = UserService(session)
    user = await user_service.get_or_create_user(callback.from_user)

    application_service = ApplicationService(session)
    application = await application_service.create_account_link_application(
        user=user,
        answers=data,
    )

    await state.clear()

    if callback.message:
        await callback.message.edit_text(
            text=(
                "✅ <b>Заявка на связку аккаунта отправлена!</b>\n\n"
                f"Номер заявки: <b>#{application.id}</b>\n\n"
                "Заявка будет рассмотрена в течение <b>1–3 недель</b>.\n\n"
                "Если за это время ничего не произойдёт, значит YouTube "
                "отклонил заявку или она не прошла по условиям."
            )
        )

    await callback.answer()

@router.callback_query(F.data == "account_link:cancel")
async def cancel_account_link_form(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.clear()

    if callback.message:
        await callback.message.edit_text(
            text="❌ Заявка на связку аккаунта отменена."
        )

    await callback.answer()

@router.callback_query(F.data == "account_link:back")
async def back_account_link_form(
    callback: CallbackQuery,
    state: FSMContext,
):
    current_state = await state.get_state()

    if current_state == AccountLinkStates.artist_nickname.state:
        await state.clear()

        if callback.message:
            await callback.message.edit_text(
                text=ACCOUNT_LINK_TERMS_TEXT,
                reply_markup=account_link_terms_keyboard(),
            )

    elif current_state == AccountLinkStates.topic_channel_link.state:
        await state.set_state(AccountLinkStates.artist_nickname)

        if callback.message:
            await callback.message.edit_text(
                text=(
                    "🎤 <b>Шаг 1/5</b>\n\n"
                    "Введите никнейм артиста."
                ),
                reply_markup=account_link_step_keyboard(),
            )

    elif current_state == AccountLinkStates.main_channel_link.state:
        await state.set_state(AccountLinkStates.topic_channel_link)

        if callback.message:
            await callback.message.edit_text(
                text=(
                    "📺 <b>Шаг 2/5</b>\n\n"
                    "Отправьте ссылку на topic-канал."
                ),
                reply_markup=account_link_step_keyboard(),
            )

    elif current_state == AccountLinkStates.topic_videos_links.state:
        await state.set_state(AccountLinkStates.main_channel_link)

        if callback.message:
            await callback.message.edit_text(
                text=(
                    "📺 <b>Шаг 3/5</b>\n\n"
                    "Отправьте ссылку на основной канал."
                ),
                reply_markup=account_link_step_keyboard(),
            )

    elif current_state == AccountLinkStates.main_videos_links.state:
        await state.set_state(AccountLinkStates.topic_videos_links)

        if callback.message:
            await callback.message.edit_text(
                text=(
                    "🎬 <b>Шаг 4/5</b>\n\n"
                    "Отправьте 3 ссылки на видео с topic-канала.\n\n"
                    "Можно отправить каждую ссылку с новой строки."
                ),
                reply_markup=account_link_step_keyboard(),
            )

    elif current_state == AccountLinkStates.preview.state:
        await state.set_state(AccountLinkStates.main_videos_links)

        if callback.message:
            await callback.message.edit_text(
                text=(
                    "🎬 <b>Шаг 5/5</b>\n\n"
                    "Отправьте 3 ссылки на видео с основного канала.\n\n"
                    "Можно отправить каждую ссылку с новой строки."
                ),
                reply_markup=account_link_step_keyboard(),
            )

    await callback.answer()


def build_account_link_preview(data: dict) -> str:
    return (
        "📋 <b>Проверьте заявку перед отправкой</b>\n\n"
        f"🎤 <b>Никнейм артиста:</b>\n{data.get('artist_nickname')}\n\n"
        f"📺 <b>Topic-канал:</b>\n{data.get('topic_channel_link')}\n\n"
        f"📺 <b>Основной канал:</b>\n{data.get('main_channel_link')}\n\n"
        f"🎬 <b>3 видео с topic-канала:</b>\n{data.get('topic_videos_links')}\n\n"
        f"🎬 <b>3 видео с основного канала:</b>\n{data.get('main_videos_links')}\n\n"
        "Если всё верно — нажмите <b>Отправить заявку</b>."
    )
