from pydantic import BaseModel
from typing import Optional, List
from .Pagination import Pagination
from .Artifact import Artifact

class TaskArtifactsListResponse(BaseModel):
    artifacts: Optional[List[Artifact]] = None
    pagination: Optional[Pagination] = None
