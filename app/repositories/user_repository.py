from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.utils.querytools import (
    fetch_first_by_stmt,
    get_scalar_one_result,
)
from app.db.enums import UserRole

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        return await fetch_first_by_stmt(self.session, stmt)

    async def create(self, telegram_id: int, username: str | None, full_name: str) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
        )

        self.session.add(user)
        await self.session.flush()

        return user
    
    async def update_basic_info(self, user: User, username: str | None, full_name: str) -> User:
        user.username = username
        user.full_name = full_name

        await self.session.flush()

        return user

    async def count_all(self) -> int:
        stmt = select(func.count(User.id))
        return await get_scalar_one_result(self.session, stmt)

    async def get_by_username(self, username: str) -> User | None:
        prepared_username = username.removeprefix("@").lower()

        stmt = select(User).where(
            func.lower(User.username) == prepared_username
        )

        return await fetch_first_by_stmt(self.session, stmt)

    async def update_role(
        self,
        user: User,
        role: UserRole,
    ) -> User:
        user.role = role

        await self.session.flush()

        return user
