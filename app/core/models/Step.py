from .StepRequestBody import StepRequestBody
from datetime import datetime
from pydantic import Field
from typing import List, Optional
from .Status import Status
from .Artifact import Artifact
class Step(StepRequestBody):
    created_at: datetime = Field(
        ...,
        description="The creation datetime of the task.",
        example="2023-01-01T00:00:00Z",
        json_encoders={datetime: lambda v: v.isoformat()},
    )
    modified_at: datetime = Field(
        ...,
        description="The modification datetime of the task.",
        example="2023-01-01T00:00:00Z",
        json_encoders={datetime: lambda v: v.isoformat()},
    )
    task_id: str = Field(
        ...,
        description="The ID of the task this step belongs to.",
        example="50da533e-3904-4401-8a07-c49adf88b5eb",
    )
    step_id: str = Field(
        ...,
        description="The ID of the task step.",
        example="6bb1801a-fd80-45e8-899a-4dd723cc602e",
    )
    name: Optional[str] = Field(
        None, description="The name of the task step.", example="Write to file"
    )
    status: Status = Field(
        ..., description="The status of the task step.", example="created"
    )
    output: Optional[str] = Field(
        None,
        description="Output of the task step.",
        example="I am going to use the write_to_file command and write Washington to a file called output.txt <write_to_file('output.txt', 'Washington')",
    )
    additional_output: Optional[dict] = Field(default_factory=dict)
    artifacts: Optional[List[Artifact]] = Field(
        [], description="A list of artifacts that the step has produced."
    )
    is_last: bool = Field(
        ..., description="Whether this is the last step in the task.", example=True
    )