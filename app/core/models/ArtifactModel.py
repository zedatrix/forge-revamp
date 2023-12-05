from .Base import Base
import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship
class ArtifactModel(Base):
    __tablename__ = "artifacts"

    artifact_id = Column(String, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.task_id"))
    step_id = Column(String, ForeignKey("steps.step_id"))
    agent_created = Column(Boolean, default=False)
    file_name = Column(String)
    relative_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    step = relationship("StepModel", back_populates="artifacts")
    task = relationship("TaskModel", back_populates="artifacts")