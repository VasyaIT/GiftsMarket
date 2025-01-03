from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.entrypoint.config import PostgresConfig


def new_session_maker(postgres_config: PostgresConfig) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(postgres_config.database_url)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
