import uvicorn
from fastapi import FastAPI

app = FastAPI()

from app.api.endpoints.users import users_app
from app.core.security import auth_app
from app.api.endpoints.tasks import task_app

app.include_router(users_app)
app.include_router(auth_app)
app.include_router(task_app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
