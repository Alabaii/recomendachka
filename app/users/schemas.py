from datetime import datetime, date
from typing import Literal
from uuid import UUID
from pydantic import BaseModel
# from pydantic import UUID


class SUsers(BaseModel):
    id: UUID
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
        orm_mode = True
        
class UserCreate(BaseModel):
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
        orm_mode = True
