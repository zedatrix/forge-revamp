from pydantic import BaseModel
from typing import Optional, List
from .Step import Step
from .Pagination import Pagination

class TaskStepsListResponse(BaseModel):
    steps: Optional[List[Step]] = None
    pagination: Optional[Pagination] = None