from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Messages(Base):
    message: Mapped[str] = mapped_column(nullable=False)
    answer: Mapped[str] = mapped_column(nullable=False)
    sender: Mapped[str] = mapped_column(nullable=False)
