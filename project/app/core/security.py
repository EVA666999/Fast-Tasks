from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt

auth_app = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


@auth_app.get("/protected_resource")
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username
    except jwt.ExpiredSignatureError:
        return {'message': 'токен истёк'}
    except jwt.InvalidTokenError:
        return {'message': 'неправильный токен'}