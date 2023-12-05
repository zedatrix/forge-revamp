from .. import Base
import datetime
from sqlalchemy import (
    Column,
    DateTime,
    String,
)
class ChatModel(Base):
    __tablename__ = "chat"
    msg_id = Column(String, primary_key=True, index=True)
    task_id = Column(String)
    role = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )