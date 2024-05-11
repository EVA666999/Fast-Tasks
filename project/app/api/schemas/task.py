import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TaskCreate(BaseModel):
    description: str
    completed: Optional[bool] = False


class TaskFromDB(BaseModel):
    id: Optional[int] = None
    description: str
    completed: Optional[bool] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[int] = None