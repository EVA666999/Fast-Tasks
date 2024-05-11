import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from app.db.database import Base
from sqlalchemy import Boolean

class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="tasks")

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    tasks = relationship("Task", back_populates="owner")
