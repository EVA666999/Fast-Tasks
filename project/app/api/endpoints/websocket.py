from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from app.db.models import Message
from sqlalchemy import select
from app.db.database import async_session_maker, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging

websocket_app = APIRouter()

html_path = os.path.abspath(os.path.join("project", "templates", "chat.html"))
print("HTML path:", html_path)
try:
    with open(html_path, "r") as file:
        html = file.read()
    print("Файл успешно прочитан")
except FileNotFoundError:
    print(f"Файл не найден: {html_path}")

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        await self.add_message_to_database(message)  # Add message to database
        for connection in self.active_connections:
            await connection.send_text(message)

    @staticmethod
    async def add_message_to_database(message: str):
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    await session.execute(Message.__table__.insert().values(message=message))
        except Exception as e:
            logging.error(f"Error occurred while adding message to database: {e}")

manager = ConnectionManager()

@websocket_app.get("/")
async def get():
    return FileResponse(html_path)

@websocket_app.get('/last_messages')
async def get_last_messages(session: AsyncSession = Depends(get_async_session)):
    async with session as s:
        query = select(Message).order_by(Message.id.desc()).limit(5)
        messages = await s.execute(query)
        messages_list = [{"id": msg.id, "message": msg.message} for msg in messages.scalars()]
        return messages_list

@websocket_app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
