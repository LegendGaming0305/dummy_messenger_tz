from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from .database import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sender_name: Mapped[str] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    user_counter: Mapped[int] = mapped_column(nullable=False, default=0)

class UserCounter(Base):
    __tablename__ = "user_counters"

    sender_name: Mapped[str] = mapped_column(primary_key=True, index=True)
    counter: Mapped[int] = mapped_column(nullable=False, default=0)