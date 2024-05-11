from typing import List
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str


class UserFromDB(UserCreate):
    id: int
    created_at: datetime = datetime.now()

    class Config:
        orm_mode = True
