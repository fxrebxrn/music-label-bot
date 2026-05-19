from html import escape
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.enums import UserRole
from app.db.models import Application, User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.release_repository import ReleaseRepository
from app.repositories.user_repository import UserRepository
from app.utils.formatting import (
    format_application_status,
    format_application_type,
    format_datetime,
    format_user_role,
)
from app.utils.release_formatting import (
    ARTIST_TYPE_TITLES,
    DISTRIBUTION_TITLES,
    RELEASE_FORMAT_TITLES,
)

class AdminService:
    def __init__(self, session: AsyncSession):
        self.user_repository = UserRepository(session)
        self.application_repository = ApplicationRepository(session)
        self.release_repository = ReleaseRepository(session)

    def can_admin(self, user: User) -> bool:
        return user.role == UserRole.ADMIN

    async def get_stats_text(self) -> str:
        users_count = await self.user_repository.count_all()
        applications_count = await self.application_repository.count_all()
        pending_count = await self.application_repository.count_pending_all()
        releases_count = await self.release_repository.count_all()

        return (
            "📊 <b>Статистика проекта</b>\n\n"
            f"👤 Пользователей: <b>{users_count}</b>\n"
            f"📝 Всего заявок: <b>{applications_count}</b>\n"
            f"⌛ Pending-заявок: <b>{pending_count}</b>\n"
            f"🎵 Релизов: <b>{releases_count}</b>"
        )

    async def get_archive(self) -> list[Application]:
        return await self.application_repository.get_archive(limit=20)

    async def get_application_by_id(
        self,
        application_id: int,
    ) -> Application | None:
        return await self.application_repository.get_by_id_with_user_and_moderator(
            application_id=application_id,
        )

    async def get_user_by_username(
        self,
        username: str,
    ) -> User | None:
        return await self.user_repository.get_by_username(username)

    async def set_user_role(
        self,
        user: User,
        role: UserRole,
    ) -> User:
        return await self.user_repository.update_role(
            user=user,
            role=role,
        )

    def build_admin_panel_text(self, user: User) -> str:
        return (
            "👑 <b>Админ-панель</b>\n\n"
            f"Вы вошли как: <b>{escape(user.full_name)}</b>\n"
            f"Роль: <b>{format_user_role(user.role)}</b>\n\n"
            "Выберите действие:"
        )

    def build_archive_text(
        self,
        applications: list[Application],
    ) -> str:
        if not applications:
            return (
                "📁 <b>Архив заявок</b>\n\n"
                "Заявок пока нет."
            )

        lines = [
            "📁 <b>Архив заявок</b>\n",
            "Показаны последние <b>20</b> заявок.\n",
        ]

        for application in applications:
            app_type = format_application_type(application.type)
            status = format_application_status(application.status)
            created_at = format_datetime(application.created_at)

            user = application.user
            if user:
                username = f"@{user.username}" if user.username else "без username"
                user_text = f"{escape(user.full_name)} ({escape(username)})"
            else:
                user_text = "пользователь не найден"

            lines.append(
                f"#{application.id} — <b>{app_type}</b>\n"
                f"Статус: <b>{status}</b>\n"
                f"Пользователь: {user_text}\n"
                f"Дата: {created_at}"
            )

        return "\n\n".join(lines)

    def build_application_text(
        self,
        application: Application,
    ) -> str:
        app_type = format_application_type(application.type)
        status = format_application_status(application.status)
        created_at = format_datetime(application.created_at)

        user_block = self._format_user_block(application.user)
        moderator_block = self._format_moderator_block(application)
        answers_block = self._format_answers(application)

        return (
            f"📄 <b>Заявка #{application.id}</b>\n\n"
            f"📌 <b>Тип:</b> {app_type}\n"
            f"📍 <b>Статус:</b> {status}\n"
            f"🕘 <b>Создана:</b> {created_at}\n\n"
            f"👤 <b>Пользователь</b>\n"
            f"{user_block}\n\n"
            f"🛡 <b>Модерация</b>\n"
            f"{moderator_block}\n\n"
            f"💬 <b>Ответы</b>\n\n"
            f"{answers_block}"
        )

    def build_found_user_text(
        self,
        user: User,
    ) -> str:
        username = f"@{user.username}" if user.username else "не указан"

        return (
            "👤 <b>Пользователь найден</b>\n\n"
            f"ID в базе: <b>{user.id}</b>\n"
            f"Telegram ID: <code>{user.telegram_id}</code>\n"
            f"Username: {escape(username)}\n"
            f"Имя: {escape(user.full_name)}\n"
            f"Текущая роль: <b>{format_user_role(user.role)}</b>\n\n"
            "Выберите новую роль:"
        )

    def build_role_changed_text(
        self,
        user: User,
    ) -> str:
        username = f"@{user.username}" if user.username else "не указан"

        return (
            "✅ <b>Роль пользователя обновлена</b>\n\n"
            f"Пользователь: {escape(user.full_name)}\n"
            f"Username: {escape(username)}\n"
            f"Новая роль: <b>{format_user_role(user.role)}</b>"
        )

    def _format_user_block(self, user: User | None) -> str:
        if user is None:
            return "Пользователь не найден."

        username = f"@{user.username}" if user.username else "не указан"

        return (
            f"ID в базе: <b>{user.id}</b>\n"
            f"Telegram ID: <code>{user.telegram_id}</code>\n"
            f"Username: {escape(username)}\n"
            f"Имя: {escape(user.full_name)}\n"
            f"Роль: <b>{format_user_role(user.role)}</b>"
        )

    def _format_moderator_block(self, application: Application) -> str:
        if application.moderator is None:
            return "Заявка ещё не рассмотрена."

        moderator = application.moderator
        username = f"@{moderator.username}" if moderator.username else "не указан"

        comment = application.moderator_comment or "Без комментария."

        reviewed_at = (
            format_datetime(application.reviewed_at)
            if application.reviewed_at
            else "дата не указана"
        )

        return (
            f"Модератор: {escape(moderator.full_name)} ({escape(username)})\n"
            f"Дата решения: {reviewed_at}\n"
            f"Комментарий:\n{escape(comment)}"
        )

    def _format_answers(self, application: Application) -> str:
        if application.type.value == "account_link":
            return self._format_account_link_answers(application.answers)

        if application.type.value == "release":
            return self._format_release_answers(application.answers)

        return "Нет данных."

    def _format_account_link_answers(self, answers: dict) -> str:
        return (
            f"<b>Никнейм артиста:</b>\n"
            f"{escape(str(answers.get('artist_nickname', '-')))}\n\n"
            f"<b>Topic-канал:</b>\n"
            f"{escape(str(answers.get('topic_channel_link', '-')))}\n\n"
            f"<b>Основной канал:</b>\n"
            f"{escape(str(answers.get('main_channel_link', '-')))}\n\n"
            f"<b>3 видео с topic-канала:</b>\n"
            f"{escape(str(answers.get('topic_videos_links', '-')))}\n\n"
            f"<b>3 видео с основного канала:</b>\n"
            f"{escape(str(answers.get('main_videos_links', '-')))}"
        )

    def _format_release_answers(self, answers: dict) -> str:
        distribution = DISTRIBUTION_TITLES.get(
            answers.get("distribution_type"),
            answers.get("distribution_type", "-"),
        )

        artist_type = ARTIST_TYPE_TITLES.get(
            answers.get("artist_type"),
            answers.get("artist_type", "-"),
        )

        release_format = RELEASE_FORMAT_TITLES.get(
            answers.get("release_format"),
            answers.get("release_format", "-"),
        )

        release_block = (
            f"<b>Основной артист / артисты:</b>\n"
            f"{escape(str(answers.get('main_artists', '-')))}\n\n"
        )

        if answers.get("single_track_title"):
            release_block += (
                f"<b>Название трека:</b>\n"
                f"{escape(str(answers.get('single_track_title', '-')))}\n\n"
            )
        else:
            release_block += (
                f"<b>Название релиза:</b>\n"
                f"{escape(str(answers.get('release_title', '-')))}\n\n"
                f"<b>Треки по порядку:</b>\n"
                f"{escape(str(answers.get('tracks_order', '-')))}\n\n"
            )

        explicit_text = "Да" if answers.get("has_explicit_content") else "Нет"

        return (
            f"<b>Дистрибуция:</b>\n"
            f"{escape(str(distribution))}\n\n"
            f"<b>Кем является:</b>\n"
            f"{escape(str(artist_type))}\n\n"
            f"<b>Формат релиза:</b>\n"
            f"{escape(str(release_format))}\n\n"
            f"{release_block}"
            f"<b>Ненормативная лексика:</b>\n"
            f"{explicit_text}\n\n"
            f"<b>Дата релиза:</b>\n"
            f"{escape(str(answers.get('release_date', '-')))}\n\n"
            f"<b>Жанр:</b>\n"
            f"{escape(str(answers.get('genre', '-')))}\n\n"
            f"<b>Ссылка на материалы:</b>\n"
            f"{escape(str(answers.get('materials_link', '-')))}\n\n"
            f"<b>Имя и фамилия артиста:</b>\n"
            f"{escape(str(answers.get('artist_full_name', '-')))}\n\n"
            f"<b>Комментарий:</b>\n"
            f"{escape(str(answers.get('comment', '-')))}"
        )