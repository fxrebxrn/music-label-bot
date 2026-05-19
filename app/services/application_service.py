from html import escape

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import ApplicationType, ReleaseFormat
from app.db.models import Application, User
from app.repositories.application_repository import ApplicationRepository
from app.utils.formatting import (
    format_application_status,
    format_application_type,
    format_datetime,
)
from app.utils.release_formatting import (
    format_artist_type,
    format_distribution_type,
    format_explicit,
    format_release_format,
    get_release_title_from_answers,
)


class ApplicationService:
    def __init__(self, session: AsyncSession):
        self.application_repository = ApplicationRepository(session)

    async def create_account_link_application(
        self,
        user: User,
        answers: dict,
    ) -> Application:
        return await self.application_repository.create(
            user_id=user.id,
            application_type=ApplicationType.ACCOUNT_LINK,
            answers=answers,
        )

    async def get_user_applications(
        self,
        user: User,
        limit: int = 10,
    ) -> list[Application]:
        return await self.application_repository.get_all_by_user_id(
            user_id=user.id,
            limit=limit,
        )

    async def get_user_application_by_id(
        self,
        user: User,
        application_id: int,
    ) -> Application | None:
        return await self.application_repository.get_by_id_and_user_id(
            application_id=application_id,
            user_id=user.id,
        )

    def build_applications_list_text(
        self,
        applications: list[Application],
    ) -> str:
        if not applications:
            return (
                "📝 <b>Мои заявки</b>\n\n"
                "У вас пока нет заявок."
            )

        lines = ["📝 <b>Мои заявки</b>\n"]

        for application in applications:
            app_type = format_application_type(application.type)
            status = format_application_status(application.status)
            created_at = format_datetime(application.created_at)

            lines.append(
                f"<b>#{application.id}</b> — {app_type}\n"
                f"Статус: <b>{status}</b>\n"
                f"Дата: {created_at}"
            )

        return "\n\n".join(lines)

    def build_application_details_text(
        self,
        application: Application,
    ) -> str:
        app_type = format_application_type(application.type)
        status = format_application_status(application.status)
        created_at = format_datetime(application.created_at)
        answers_text = self._format_answers(application)
        moderation_text = self._format_moderation_block(application)

        return (
            f"📄 <b>Заявка #{application.id}</b>\n\n"
            f"📌 <b>Тип:</b> {app_type}\n"
            f"📍 <b>Статус:</b> {status}\n"
            f"🕘 <b>Дата создания:</b> {created_at}\n\n"
            f"{moderation_text}\n\n"
            f"📋 <b>Ответы заявки</b>\n\n"
            f"{answers_text}"
        )

    def _format_moderation_block(self, application: Application) -> str:
        if application.moderator:
            username = (
                f"@{application.moderator.username}"
                if application.moderator.username
                else "без username"
            )
            moderator_text = (
                f"{escape(application.moderator.full_name)} "
                f"({escape(username)})"
            )
        else:
            moderator_text = "Пока нет"

        comment = application.moderator_comment or "Пока нет."

        return (
            "🛡 <b>Модерация</b>\n"
            f"Модератор: {moderator_text}\n"
            f"Комментарий: <i>{escape(comment)}</i>"
        )

    def _format_answers(self, application: Application) -> str:
        if application.type == ApplicationType.ACCOUNT_LINK:
            return self._format_account_link_answers(application.answers)

        if application.type == ApplicationType.RELEASE:
            return self._format_release_answers(application.answers)

        return "Нет данных."

    def _format_account_link_answers(self, answers: dict) -> str:
        return "\n\n".join(
            [
                self._answer("Никнейм артиста", answers.get("artist_nickname")),
                self._answer("Topic-канал", answers.get("topic_channel_link")),
                self._answer("Основной канал", answers.get("main_channel_link")),
                self._answer("3 видео с topic-канала", answers.get("topic_videos_links")),
                self._answer("3 видео с основного канала", answers.get("main_videos_links")),
            ]
        )

    def _format_release_answers(self, answers: dict) -> str:
        is_single = answers.get("release_format") == ReleaseFormat.SINGLE.value
        title_label = "Название трека" if is_single else "Название релиза"

        blocks = [
            self._answer("Дистрибуция", format_distribution_type(answers.get("distribution_type"))),
            self._answer("Кем является", format_artist_type(answers.get("artist_type"))),
            self._answer("Формат релиза", format_release_format(answers.get("release_format"))),
            self._answer(
                "Основной артист / артисты",
                answers.get("main_artists") or answers.get("track_authors"),
            ),
            self._answer(title_label, get_release_title_from_answers(answers)),
        ]

        if not is_single:
            blocks.append(self._answer("Треки по порядку", answers.get("tracks_order")))

        blocks.extend(
            [
                self._answer("Ненормативная лексика", format_explicit(answers.get("has_explicit_content"))),
                self._answer("Дата релиза", answers.get("release_date")),
                self._answer("Жанр", answers.get("genre")),
                self._answer("Ссылка на материалы", answers.get("materials_link")),
                self._answer("Имя и фамилия артиста", answers.get("artist_full_name")),
                self._answer("Комментарий", answers.get("comment") or "-"),
            ]
        )

        return "\n\n".join(blocks)

    def _answer(self, question: str, answer: object) -> str:
        safe_answer = escape(str(answer if answer not in (None, "") else "-"))
        return f"<b>{question}:</b>\n{safe_answer}"
