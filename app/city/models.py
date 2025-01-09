from sqlalchemy import UUID
import uuid
from sqlalchemy.orm import mapped_column, Mapped

from app.database import Base
from datetime import date


class City(Base):
    __tablename__ = "cities"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    country: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]

