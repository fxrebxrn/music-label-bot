from html import escape

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import (
    ApplicationStatus,
    ApplicationType,
    ReleaseFormat,
    ReleaseStatus,
    UserRole,
)
from app.db.models import Application, User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.release_repository import ReleaseRepository
from app.utils.formatting import (
    format_application_status,
    format_application_type,
    format_datetime,
    format_user_role,
)
from app.utils.release_formatting import (
    format_artist_type,
    format_distribution_type,
    format_explicit,
    format_release_format,
    get_release_title_from_answers,
)


class ModerationService:
    def __init__(self, session: AsyncSession):
        self.application_repository = ApplicationRepository(session)
        self.release_repository = ReleaseRepository(session)

    def can_moderate(self, user: User) -> bool:
        return user.role in (UserRole.MODERATOR, UserRole.ADMIN)

    async def get_pending_applications(self) -> list[Application]:
        return await self.application_repository.get_pending(limit=10)

    async def get_application_for_moderation(
        self,
        application_id: int,
    ) -> Application | None:
        return await self.application_repository.get_by_id_with_user(
            application_id=application_id,
        )

    async def approve_application(
        self,
        application: Application,
        moderator: User,
        moderator_comment: str | None,
    ) -> Application:
        await self.application_repository.review(
            application=application,
            status=ApplicationStatus.APPROVED,
            moderator=moderator,
            moderator_comment=self._clean_comment(moderator_comment),
        )

        if application.type == ApplicationType.RELEASE and application.release_id:
            await self.release_repository.update_status_by_id(
                release_id=application.release_id,
                status=ReleaseStatus.APPROVED,
            )

        return application

    async def reject_application(
        self,
        application: Application,
        moderator: User,
        moderator_comment: str | None,
    ) -> Application:
        await self.application_repository.review(
            application=application,
            status=ApplicationStatus.REJECTED,
            moderator=moderator,
            moderator_comment=self._clean_comment(moderator_comment),
        )

        if application.type == ApplicationType.RELEASE and application.release_id:
            await self.release_repository.update_status_by_id(
                release_id=application.release_id,
                status=ReleaseStatus.REJECTED,
            )

        return application

    def build_user_decision_notification(
        self,
        application: Application,
        moderator: User,
    ) -> str:
        status = format_application_status(application.status)
        app_type = format_application_type(application.type)
        comment = application.moderator_comment or "Без комментария."

        return (
            f"📬 <b>По вашей заявке принято решение</b>\n\n"
            f"📄 <b>Заявка:</b> #{application.id}\n"
            f"📌 <b>Тип:</b> {app_type}\n"
            f"📍 <b>Статус:</b> {status}\n"
            f"💬 <b>Комментарий модератора:</b>\n"
            f"{escape(comment)}"
        )

    def build_queue_text(self, applications: list[Application]) -> str:
        if not applications:
            return (
                "🛡 <b>Модерация</b>\n\n"
                "Очередь пуста. Pending-заявок сейчас нет."
            )

        lines = [
            "🛡 <b>Модерация</b>",
            f"Заявок в очереди: <b>{len(applications)}</b>",
        ]

        for application in applications:
            app_type = format_application_type(application.type)
            status = format_application_status(application.status)
            created_at = format_datetime(application.created_at)
            user = application.user
            username = f"@{user.username}" if user and user.username else "Без username"

            lines.append(
                f"<b>#{application.id}</b> — {app_type}\n"
                f"Пользователь: {escape(username)}\n"
                f"Статус: <b>{status}</b>\n"
                f"Дата: {created_at}"
            )

        return "\n\n".join(lines)

    def build_application_text(
        self,
        application: Application,
    ) -> str:
        user = application.user
        app_type = format_application_type(application.type)
        status = format_application_status(application.status)
        created_at = format_datetime(application.created_at)
        answers_text = self._format_answers(application)

        if user:
            username = f"@{user.username}" if user.username else "Не указан"
            user_block = (
                f"🆔 <b>Telegram ID:</b> <code>{user.telegram_id}</code>\n"
                f"🔗 <b>Username:</b> {escape(username)}\n"
                f"👤 <b>Имя:</b> {escape(user.full_name)}\n"
                f"🛡 <b>Роль:</b> {format_user_role(user.role)}"
            )
        else:
            user_block = "Пользователь не найден."

        return (
            f"📄 <b>Заявка #{application.id}</b>\n\n"
            f"📌 <b>Тип:</b> {app_type}\n"
            f"📍 <b>Статус:</b> {status}\n"
            f"🕘 <b>Дата создания:</b> {created_at}\n\n"
            f"👤 <b>Пользователь</b>\n"
            f"{user_block}\n\n"
            f"📋 <b>Ответы заявки</b>\n\n"
            f"{answers_text}"
        )

    def _format_answers(self, application: Application) -> str:
        answers = application.answers

        if application.type == ApplicationType.ACCOUNT_LINK:
            return "\n\n".join(
                [
                    self._answer("Никнейм артиста", answers.get("artist_nickname")),
                    self._answer("Topic-канал", answers.get("topic_channel_link")),
                    self._answer("Основной канал", answers.get("main_channel_link")),
                    self._answer("3 видео с topic-канала", answers.get("topic_videos_links")),
                    self._answer("3 видео с основного канала", answers.get("main_videos_links")),
                ]
            )

        if application.type == ApplicationType.RELEASE:
            return self._format_release_answers(answers)

        return "Нет ответов."

    def _format_release_answers(self, answers: dict) -> str:
        is_single = answers.get("release_format") == ReleaseFormat.SINGLE.value
        title_label = "Название трека" if is_single else "Название релиза"

        blocks = [
            self._answer("Какая дистрибуция", format_distribution_type(answers.get("distribution_type"))),
            self._answer("Кем вы являетесь", format_artist_type(answers.get("artist_type"))),
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
                self._answer("Есть ли ненормативная лексика", format_explicit(answers.get("has_explicit_content"))),
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
        return f"<b>Q:</b> {question}\n<b>A:</b> {safe_answer}"

    def _clean_comment(self, value: str | None) -> str | None:
        if not value:
            return None

        value = value.strip()
        if not value or value == "-":
            return None

        return value
