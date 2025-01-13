from sqlalchemy import UUID, String
import uuid
from sqlalchemy.orm import mapped_column, Mapped

from app.database import Base
from datetime import date


class City(Base):
    __tablename__ = "cities"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]= mapped_column(String,unique=True)
    country: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]

