from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.api.schemas.user import UserCreate, UserFromDB
from urllib.parse import unquote
from app.core.security import *
from app.db.database import async_session_maker
from app.db.models import Users

users_app = APIRouter()

users_db = []

@users_app.post("/auth/register/", response_model=UserFromDB)
async def create_todo(user: UserCreate):
    async with async_session_maker() as session:
        new_user = Users(username=user.username, password=user.password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
async def find_user_by_username(username: str):
    async with async_session_maker() as session:
        result = await session.execute(select(Users).filter(Users.username == username))
        return result.scalars().first()

@users_app.post('/auth/login/')
async def login(login_user: UserCreate):
    current_user = await find_user_by_username(login_user.username)
    if current_user:
        return {"access_token": create_jwt_token({"sub": login_user.username}), "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")