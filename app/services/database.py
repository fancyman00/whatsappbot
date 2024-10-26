from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.models.database import Base

engine = create_async_engine(settings.DATABASE.database_url)

AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with AsyncSessionFactory() as session:
        yield session


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
