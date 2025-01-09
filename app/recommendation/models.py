from typing import Literal
import uuid
from sqlalchemy import UUID,  Date, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from app.database import Base
from datetime import date

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    recommended_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    similarity: Mapped[float]