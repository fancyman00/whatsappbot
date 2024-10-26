from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid
from datetime import datetime, timezone


class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone.utc), nullable=False
    )
    __name__: str

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

    async def save(self, db_session: AsyncSession) -> None:
        try:
            db_session.add(self)
            await db_session.commit()
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex

    async def delete(self, db_session: AsyncSession) -> bool:
        try:
            db_session.delete(self)
            await db_session.commit()
            return True
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex

    async def save_or_update(self, db_session: AsyncSession, **kwargs) -> Any:
        stmt = select(type(self)).filter_by(**kwargs)
        result = await db_session.execute(stmt)
        db_instance = result.scalars().first()

        try:
            if db_instance:
                for key, value in kwargs.items():
                    setattr(db_instance, key, value)
            else:
                db_session.add(self)

            await db_session.commit()
            return db_instance
        except SQLAlchemyError as ex:
            await db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex
