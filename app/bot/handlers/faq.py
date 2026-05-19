from aiogram import F, Router
from aiogram.types import Message
from app.bot.keyboards.faq import faq_keyboard
from app.services.faq_service import FaqService

router = Router()

@router.message(F.text == "FAQ")
async def faq_handler(message: Message):
    faq_service = FaqService()

    await message.answer(
        text=faq_service.build_main_text(),
        reply_markup=faq_keyboard(faq_service.get_links()),
    )
