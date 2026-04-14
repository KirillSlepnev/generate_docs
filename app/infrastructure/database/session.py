from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings


engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_maker = async_sessionmaker(engine, expire_on_commit=True)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
