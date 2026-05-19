from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import settings

engine = create_async_engine(url=settings.database_url, echo=settings.debug)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
