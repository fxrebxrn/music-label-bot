from datetime import date, datetime
from typing import Optional
from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SqlEnum
from app.db.base import Base
from app.db.enums import (
    ApplicationStatus,
    ApplicationType,
    ArtistType,
    DistributionType,
    ReleaseFormat,
    ReleaseStatus,
    UserRole,
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, name="user_role"), default=UserRole.ARTIST, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    applications: Mapped[list["Application"]] = relationship(back_populates="user", foreign_keys="Application.user_id")
    releases: Mapped[list["Release"]] = relationship(back_populates="user")

class Release(Base):
    __tablename__ = "releases"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    distribution_type: Mapped[DistributionType] = mapped_column(SqlEnum(DistributionType, name="distribution_type"), nullable=False)
    artist_type: Mapped[ArtistType] = mapped_column(SqlEnum(ArtistType, name="artist_type"), nullable=False)
    release_format: Mapped[ReleaseFormat] = mapped_column(SqlEnum(ReleaseFormat, name="release_format"), nullable=False)
    has_explicit_content: Mapped[bool] = mapped_column(default=False, nullable=False)
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    genre: Mapped[str] = mapped_column(String(100), nullable=False)
    materials_link: Mapped[str] = mapped_column(Text, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tracks_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    artists_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[ReleaseStatus] = mapped_column(SqlEnum(ReleaseStatus, name="release_status"), default=ReleaseStatus.PENDING, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="releases")
    applications: Mapped[list["Application"]] = relationship(back_populates="release")

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    release_id: Mapped[Optional[int]] = mapped_column(ForeignKey("releases.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[ApplicationType] = mapped_column(SqlEnum(ApplicationType, name="application_type"), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(SqlEnum(ApplicationStatus, name="application_status"), default=ApplicationStatus.PENDING, nullable=False)
    answers: Mapped[dict] = mapped_column(JSONB, nullable=False)
    moderator_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    moderator_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="applications", foreign_keys=[user_id])
    release: Mapped[Optional["Release"]] = relationship(back_populates="applications")
    moderator: Mapped[Optional["User"]] = relationship(foreign_keys=[moderator_id])
