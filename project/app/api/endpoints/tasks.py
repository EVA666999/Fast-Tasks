from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy import select
from app.api.schemas.task import TaskCreate, TaskFromDB
from app.core.security import *
from app.db.database import async_session_maker
from app.db.models import Task, Users
from typing import List
from sqlalchemy import update
from app.api.endpoints.websocket import manager as websocket_manager

task_app = APIRouter()

@task_app.post("/create", response_model=TaskFromDB)
async def create_todo(task: TaskCreate, current_username: str = Depends(get_user_from_token)):
    """
    Создает новую задачу.

    Parameters:
    - task: Данные для новой задачи.
    - current_username: Имя текущего пользователя.

    Raises:
    - HTTPException(404): Если пользователь не найден.

    Returns:
    - TaskFromDB: Новая задача.
    """
    async with async_session_maker() as session:
        user = await session.execute(select(Users).filter(Users.username == current_username))
        user = user.scalar_one_or_none()
        if user:
            new_task = Task(description=task.description, completed=task.completed, owner_id=user.id)
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)
            # Отправляем информацию о новой задаче всем подключенным клиентам WebSocket
            await websocket_manager.broadcast(f"Создана новая задача: {new_task.description}, от пользователя: {current_username}")
            return new_task
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@task_app.get("/tasks", response_model=List[TaskFromDB])
async def get_tasks(current_user: str = Depends(get_user_from_token)):
    """
    Получает список задач текущего пользователя.

    Parameters:
    - current_user: Имя текущего пользователя.

    Returns:
    - List[TaskFromDB]: Список задач.
    """
    async with async_session_maker() as session:
        user = await session.execute(select(Users).filter(Users.username == current_user))
        user = user.scalar_one_or_none()
        if user:
            tasks = await session.execute(select(Task).filter(Task.owner_id == user.id))
            return tasks.scalars().all()


@task_app.put('/task/{task_id}', response_model=TaskFromDB)
async def patch_task(task_id: int, updated_task: TaskCreate, current_user: str = Depends(get_user_from_token)):
    """
    Изменяет задачу по ее ID.

    Parameters:
    - task_id: ID задачи для изменения.
    - updated_task: Обновленные данные задачи.
    - current_user: Имя текущего пользователя.

    Raises:
    - HTTPException(403): Если нет прав на изменение задачи.
    - HTTPException(404): Если задача не найдена.

    Returns:
    - TaskFromDB: Обновленная задача.
    """
    async with async_session_maker() as session:
        async with session.begin():
            user = await session.execute(select(Users).filter(Users.username == current_user))
            user = user.scalar_one_or_none()
            
            task = await session.execute(select(Task).filter(Task.id == task_id))
            task_for_put = task.scalar_one_or_none()
            
            if task_for_put:
                if task_for_put.owner_id == user.id:
                    task_for_put.description = updated_task.description
                    task_for_put.completed = updated_task.completed
                    await websocket_manager.broadcast(f"Задача: {task_for_put.description}, от пользователя: {user.username} изменена на {updated_task}")
                    await session.commit()
                    return updated_task
                else:
                    raise HTTPException(status_code=403, detail="У вас нет разрешения на изменение этой задачи")
            else:
                raise HTTPException(status_code=404, detail="Задача не найдена")
            

@task_app.delete('/task/{task_id}', response_model=dict)
async def delete_task(task_id: int, current_user: str = Depends(get_user_from_token)):
    """
    Удаляет задачу по ее ID.

    Parameters:
    - task_id: ID задачи для удаления.
    - current_user: Имя текущего пользователя.

    Raises:
    - HTTPException(403): Если нет прав на удаление задачи.
    - HTTPException(404): Если задача не найдена.
        
    Returns:
    - dict: Сообщение об успешном удалении задачи.
    """
    async with async_session_maker() as session:
        async with session.begin():
            user = await session.execute(select(Users).filter(Users.username == current_user))
            user = user.scalar_one_or_none()
            task = await session.execute(select(Task).filter(Task.id == task_id))
            task_for_del = task.scalar_one_or_none()
            await websocket_manager.broadcast(f"Задача с id: {task_id}, от пользователя: {user.username} удалена")
            if not task_for_del:
                raise HTTPException(status_code=404, detail="Task not found")
            if task_for_del.owner_id != user.id:
                raise HTTPException(status_code=403, detail="You are not allowed to delete this task")
            await session.delete(task_for_del)

    return {"message": "Task deleted successfully"}
