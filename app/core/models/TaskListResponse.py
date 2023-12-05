from pydantic import BaseModel
from typing import Optional, List
from .Task import Task
from .Pagination import Pagination

class TaskListResponse(BaseModel):
    tasks: Optional[List[Task]] = None
    pagination: Optional[Pagination] = None