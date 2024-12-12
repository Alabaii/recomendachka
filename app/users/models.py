
from typing import TYPE_CHECKING, Literal
import uuid
from sqlalchemy import UUID, Column, Date, DateTime, Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.database import Base
from datetime import date


# Модель написана в соответствии с современным стилем Алхимии (версии 2.x)
class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str]
    surname: Mapped[str]
    date_created: Mapped[date] = mapped_column(Date)
    description: Mapped[str]
    birtday: Mapped[date] = mapped_column(Date)
    gender: Mapped[Literal["man","woman"]]
    city: Mapped[str]

