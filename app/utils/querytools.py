from sqlalchemy.ext.asyncio import AsyncSession

async def fetch_all_by_stmt(session: AsyncSession, stmt):
    result = await session.execute(stmt)
    return result.scalars().all()

async def fetch_first_by_stmt(session: AsyncSession, stmt):
    result = await session.execute(stmt)
    return result.scalars().first()

async def get_scalar_result(session: AsyncSession, stmt):
    result = await session.execute(stmt)
    return result.scalar()

async def get_scalar_one_result(session: AsyncSession, stmt):
    result = await session.execute(stmt)
    return result.scalar_one()
