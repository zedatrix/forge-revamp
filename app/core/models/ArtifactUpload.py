from pydantic import BaseModel, Field

class ArtifactUpload(BaseModel):
    file: str = Field(..., description="File to upload.", format="binary")
    relative_path: str = Field(
        ...,
        description="Relative path of the artifact in the agent's workspace.",
        example="python/code",
    )