from pydantic import BaseModel, Field
from typing import Optional, List

class TaskRequestBody(BaseModel):
    name: Optional[str] = Field(
        None, description="The name of the task step.", example="Write to file"
    )
    input: str = Field(
        ...,
        min_length=1,
        description="Input prompt for the task.",
        example="Write the words you receive to the file 'output.txt'.",
    )
    additional_input: Optional[dict] = {}