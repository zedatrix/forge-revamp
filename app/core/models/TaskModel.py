from .Base import Base
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    String,
)
import datetime
from sqlalchemy.orm import relationship

class TaskModel(Base):
    __tablename__ = "tasks"

    task_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    input = Column(String)
    status = Column(String)
    output = Column(String)
    additional_input = Column(JSON)
    additional_output = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    artifacts = relationship("ArtifactModel", back_populates="task")