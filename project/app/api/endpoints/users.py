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
async def create_user(user: UserCreate):
    """
    Регистрирует нового пользователя.

    Parameters:
    - user: Данные для регистрации нового пользователя.

    Returns:
    - UserFromDB: Зарегистрированный пользователь.
    """
    async with async_session_maker() as session:
        new_user = Users(username=user.username, password=user.password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
async def find_user_by_username(username: str):
    """
    Находит пользователя по его имени пользователя.

    Parameters:
    - username: Имя пользователя для поиска.

    Returns:
    - Users: Найденный пользователь или None, если пользователь не найден.
    """
    async with async_session_maker() as session:
        result = await session.execute(select(Users).filter(Users.username == username))
        return result.scalars().first()

@users_app.post('/auth/login/')
async def login(login_user: UserCreate):
    """
    Авторизует пользователя.

    Parameters:
    - login_user: Данные пользователя для входа.

    Raises:
    - HTTPException(401): Если учетные данные неверны.

    Returns:
    - dict: Токен доступа к API.
    """
    current_user = await find_user_by_username(login_user.username)
    if current_user:
        return {"access_token": create_jwt_token({"sub": login_user.username}), "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")