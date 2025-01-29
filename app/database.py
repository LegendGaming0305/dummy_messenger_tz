from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import AsyncGenerator

from .settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, isolation_level="SERIALIZABLE")
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    repr_cols_num = 2
    repr_cols = tuple()
    
    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

async def get_async_session():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()