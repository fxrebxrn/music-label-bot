from app.config import settings

class FaqService:
    FAQ_LINKS = {
        "royalty": {
            "title": "💰 Информация о выплатах роялти",
            "url": settings.faq_link_royalty,
        },
        "privacy": {
            "title": "🔒 Политика конфиденциальности",
            "url": settings.faq_link_privacy,
        },
        "terms": {
            "title": "📄 Условия использования",
            "url": settings.faq_link_terms,
        },
    }

    def get_links(self) -> dict:
        return self.FAQ_LINKS

    def build_main_text(self) -> str:
        return (
            "❓ <b>FAQ и важная информация</b>\n\n"
            "Здесь собраны основные документы и правила работы с лейблом.\n\n"
            "Выберите нужный раздел ниже:"
        )