from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Release
from app.utils.querytools import get_scalar_result
from typing import Any
from datetime import date
from app.db.enums import DistributionType, ArtistType, ReleaseFormat, ReleaseStatus

class ReleaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_by_user_id(self, user_id: int) -> int:
        stmt = select(func.count(Release.id)).where(Release.user_id == user_id)
        return await get_scalar_result(self.session, stmt)

    async def update_status_by_id(
        self,
        release_id: int,
        status: ReleaseStatus,
    ) -> None:
        stmt = select(Release).where(Release.id == release_id)
        result = await self.session.execute(stmt)
        release = result.scalars().first()

        if release is None:
            return

        release.status = status
        await self.session.flush()

    async def create(
        self,
        user_id: int,
        title: str,
        distribution_type: DistributionType,
        artist_type: ArtistType,
        release_format: ReleaseFormat,
        has_explicit_content: bool,
        release_date: date,
        genre: str,
        materials_link: str,
        tracks_data: dict[str, Any],
        artists_data: dict[str, Any],
        comment: str | None,
    ) -> Release:
        release = Release(
            user_id=user_id,
            title=title,
            distribution_type=distribution_type,
            artist_type=artist_type,
            release_format=release_format,
            has_explicit_content=has_explicit_content,
            release_date=release_date,
            genre=genre,
            materials_link=materials_link,
            tracks_data=tracks_data,
            artists_data=artists_data,
            comment=comment,
        )

        self.session.add(release)
        await self.session.flush()

        return release

    async def count_all(self) -> int:
        stmt = select(func.count(Release.id))
        result = await self.session.execute(stmt)
        return result.scalar_one()
