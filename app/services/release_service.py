from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import (
    ApplicationType,
    ArtistType,
    DistributionType,
    ReleaseFormat,
)
from app.db.models import Application, User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.release_repository import ReleaseRepository


class ReleaseService:
    def __init__(self, session: AsyncSession):
        self.release_repository = ReleaseRepository(session)
        self.application_repository = ApplicationRepository(session)

    async def create_release_application(
        self,
        user: User,
        data: dict,
    ) -> Application:
        release_format = ReleaseFormat(data["release_format"])
        release_title = self._get_release_title(data)
        tracks_data = self._build_tracks_data(data)
        artists_data = self._build_artists_data(data)

        release = await self.release_repository.create(
            user_id=user.id,
            title=release_title,
            distribution_type=DistributionType(data["distribution_type"]),
            artist_type=ArtistType(data["artist_type"]),
            release_format=release_format,
            has_explicit_content=data["has_explicit_content"],
            release_date=self._parse_release_date(data["release_date"]),
            genre=data["genre"],
            materials_link=data["materials_link"],
            tracks_data=tracks_data,
            artists_data=artists_data,
            comment=self._clean_comment(data.get("comment")),
        )

        application = await self.application_repository.create(
            user_id=user.id,
            application_type=ApplicationType.RELEASE,
            answers=data,
            release_id=release.id,
        )

        return application

    def _get_release_title(self, data: dict) -> str:
        return data.get("release_title") or data.get("single_track_title")

    def _build_tracks_data(self, data: dict) -> dict:
        if data["release_format"] == ReleaseFormat.SINGLE.value:
            return {
                "tracks": [
                    {
                        "number": 1,
                        "title": self._get_release_title(data),
                    }
                ]
            }

        tracks = []

        for index, line in enumerate(data["tracks_order"].splitlines(), start=1):
            title = line.strip()

            if title:
                tracks.append(
                    {
                        "number": index,
                        "title": title,
                    }
                )

        return {"tracks": tracks}

    def _build_artists_data(self, data: dict) -> dict:
        main_artists = self._split_lines_or_commas(data.get("main_artists"))

        return {
            "main_artists": main_artists,
            "authors": main_artists,
            "artist_full_name": data["artist_full_name"],
        }

    def _split_lines_or_commas(self, value: str | None) -> list[str]:
        if not value:
            return []

        prepared = value.replace(",", "\n")

        return [
            item.strip()
            for item in prepared.splitlines()
            if item.strip()
        ]

    def _parse_release_date(self, value: str):
        return datetime.strptime(value, "%d.%m.%Y").date()

    def _clean_comment(self, value: str | None) -> str | None:
        if not value:
            return None

        value = value.strip()

        if not value or value == "-":
            return None

        return value
