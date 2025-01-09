from typing import Literal
from uuid import UUID
from pydantic import BaseModel


class SCity(BaseModel):
    id: UUID
    name: str
    country: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True