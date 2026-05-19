from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.release_repository import ReleaseRepository
from app.utils.formatting import (
    format_application_status,
    format_application_type,
    format_datetime,
    format_user_role,
)

class ProfileService:
    def __init__(self, session: AsyncSession):
        self.application_repository = ApplicationRepository(session)
        self.release_repository = ReleaseRepository(session)

    def _format_latest_applications(self, applications: list) -> str:
        if not applications:
            return "Пока заявок нет."

        lines = []

        for application in applications:
            app_type = format_application_type(application.type)
            status = format_application_status(application.status)
            created_at = format_datetime(application.created_at)

            lines.append(
                f"#{application.id} — {app_type} — {status}\n"
                f"Дата: {created_at}"
            )

        return "\n\n".join(lines)

    async def get_profile_text(self, user: User) -> str:
        applications_count = await self.application_repository.count_by_user_id(
            user_id=user.id,
        )

        releases_count = await self.release_repository.count_by_user_id(
            user_id=user.id,
        )

        pending_applications_count = (
            await self.application_repository.count_pending_by_user_id(
                user_id=user.id,
            )
        )

        latest_applications = await self.application_repository.get_latest_by_user_id(
            user_id=user.id,
            limit=5,
        )

        latest_applications_text = self._format_latest_applications(
            latest_applications,
        )

        username = f"@{user.username}" if user.username else "Не указан"

        return (
            "👤 <b>Профиль</b>\n\n"
            f"🆔 <b>Telegram ID:</b> <code>{user.telegram_id}</code>\n"
            f"🔗 <b>Username:</b> {username}\n"
            f"🛡 <b>Роль:</b> {format_user_role(user.role)}\n\n"
            f"📝 Всего заявок: <b>{applications_count}</b>\n"
            f"🎵 Всего релизов: <b>{releases_count}</b>\n"
            f"⌛ На модерации: <b>{pending_applications_count}</b>\n\n"
            "🕘 <b>Последние заявки</b>\n"
            f"{latest_applications_text}"
        )
