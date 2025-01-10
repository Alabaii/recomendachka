from datetime import date
from typing import Literal
from uuid import UUID
from pydantic import BaseModel


class SUser(BaseModel):
    first_name: str
    surname: str
    date_created: date
    description: str
    birthday: date
    gender: Literal["man","woman"]
    city: str
    profession : str
    experience : float


    class Config:
        from_attributes = True
