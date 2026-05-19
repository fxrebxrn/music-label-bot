from sqlalchemy import desc, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.enums import ApplicationStatus, ApplicationType
from app.db.models import Application, User
from app.utils.querytools import (
    fetch_all_by_stmt,
    fetch_first_by_stmt,
    get_scalar_one_result,
    get_scalar_result,
)
from datetime import datetime, timezone

class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_pending(
        self,
        limit: int = 10,
    ) -> list[Application]:
        stmt = (
            select(Application)
            .options(selectinload(Application.user), selectinload(Application.moderator))
            .where(Application.status == ApplicationStatus.PENDING)
            .order_by(desc(Application.created_at))
            .limit(limit)
        )

        return list(await fetch_all_by_stmt(self.session, stmt))

    async def get_by_id_with_user(
        self,
        application_id: int,
    ) -> Application | None:
        stmt = (
            select(Application)
            .options(selectinload(Application.user), selectinload(Application.moderator))
            .where(Application.id == application_id)
        )

        return await fetch_first_by_stmt(self.session, stmt)

    async def review(
        self,
        application: Application,
        status: ApplicationStatus,
        moderator: User,
        moderator_comment: str | None,
    ) -> Application:
        application.status = status
        application.moderator_id = moderator.id
        application.moderator_comment = moderator_comment
        application.reviewed_at = datetime.now(timezone.utc)

        await self.session.flush()

        return application

    async def update_status(
        self,
        application: Application,
        status: ApplicationStatus,
    ) -> Application:
        application.status = status

        await self.session.flush()

        return application

    async def count_by_user_id(self, user_id: int) -> int:
        stmt = select(func.count(Application.id)).where(Application.user_id == user_id)
        return await get_scalar_result(self.session, stmt)

    async def count_pending_by_user_id(self, user_id: int) -> int:
        stmt = select(func.count(Application.id)).where(Application.user_id == user_id, Application.status == ApplicationStatus.PENDING)
        return await get_scalar_result(self.session, stmt)

    async def get_latest_by_user_id(self, user_id: int, limit: int = 5) -> list[Application]:
        stmt = (select(Application).where(Application.user_id == user_id).order_by(desc(Application.created_at)).limit(limit))
        return list(await fetch_all_by_stmt(self.session, stmt))
    
    async def get_all_by_user_id(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[Application]:
        stmt = (
            select(Application)
            .options(selectinload(Application.moderator))
            .where(Application.user_id == user_id)
            .order_by(desc(Application.created_at))
            .limit(limit)
        )

        return list(await fetch_all_by_stmt(self.session, stmt))

    async def get_by_id_and_user_id(
        self,
        application_id: int,
        user_id: int,
    ) -> Application | None:
        stmt = (
            select(Application)
            .options(selectinload(Application.moderator))
            .where(
            Application.id == application_id,
            Application.user_id == user_id,
        )
        )

        return await fetch_first_by_stmt(self.session, stmt)

    async def create(self,
        user_id: int,
        application_type: ApplicationType,
        answers: dict,
        status: ApplicationStatus = ApplicationStatus.PENDING,
        release_id: int | None = None,
    ) -> Application:
        application = Application(
            user_id=user_id,
            release_id=release_id,
            type=application_type,
            status=status,
            answers=answers,
        )

        self.session.add(application)
        await self.session.flush()

        return application

    async def count_all(self) -> int:
        stmt = select(func.count(Application.id))
        return await get_scalar_one_result(self.session, stmt)

    async def count_pending_all(self) -> int:
        stmt = select(func.count(Application.id)).where(
            Application.status == ApplicationStatus.PENDING,
        )
        return await get_scalar_one_result(self.session, stmt)

    async def get_archive(
        self,
        limit: int = 20,
    ) -> list[Application]:
        stmt = (
            select(Application)
            .options(selectinload(Application.user))
            .order_by(desc(Application.created_at))
            .limit(limit)
        )

        return list(await fetch_all_by_stmt(self.session, stmt))

    async def get_by_id_with_user_and_moderator(
        self,
        application_id: int,
    ) -> Application | None:
        stmt = (
            select(Application)
            .options(
                selectinload(Application.user),
                selectinload(Application.moderator),
            )
            .where(Application.id == application_id)
        )

        return await fetch_first_by_stmt(self.session, stmt)
