from .Base import Base
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    String,
    ForeignKey,
    Boolean
)
import datetime
from sqlalchemy.orm import relationship
class StepModel(Base):
    __tablename__ = "steps"

    step_id = Column(String, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.task_id"))
    name = Column(String)
    input = Column(String)
    status = Column(String)
    output = Column(String)
    is_last = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    additional_input = Column(JSON)
    additional_output = Column(JSON)
    artifacts = relationship("ArtifactModel", back_populates="step")