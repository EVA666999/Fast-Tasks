from fastapi import FastAPI
import uvicorn

app = FastAPI()

from app.api.endpoints.users import users_app
from app.core.security import auth_app
from app.api.endpoints.tasks import task_app
from app.api.endpoints.websocket import websocket_app

app.include_router(users_app)
app.include_router(auth_app)
app.include_router(task_app)
app.include_router(websocket_app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

