from .core import AgentDB, ForgeLogger, NotFoundError
from .core.models.Chat import ChatModel
from sqlalchemy.exc import SQLAlchemyError
import uuid

LOG = ForgeLogger(__name__)
#TODO add more database related methods
class ForgeDatabase(AgentDB):

    async def add_chat_history(self, task_id, messages):
        for message in messages:
            await self.add_chat_message(task_id, message['role'], message['content'])

    async def add_chat_message(self, task_id, role, content):
        if self.debug_enabled:
            LOG.debug("Creating new chat message")
        try:
            with self.Session() as session:
                mew_msg = ChatModel(
                    msg_id=str(uuid.uuid4()),
                    task_id=task_id,
                    role=role,
                    content=content,
                )
                session.add(mew_msg)
                session.commit()
                session.refresh(mew_msg)
                if self.debug_enabled:
                    LOG.debug(f"Created new Chat message with task_id: {mew_msg.msg_id}")
                return mew_msg
        except SQLAlchemyError as e:
            LOG.error(f"SQLAlchemy error while creating task: {e}")
            raise
        except NotFoundError as e:
            raise
        except Exception as e:
            LOG.error(f"Unexpected error while creating task: {e}")
            raise

    async def get_chat_history(self, task_id):
        if self.debug_enabled:
            LOG.debug(f"Getting chat history with task_id: {task_id}")
        try:
            with self.Session() as session:
                if messages := (
                    session.query(ChatModel)
                    .filter(ChatModel.task_id == task_id)
                    .order_by(ChatModel.created_at)
                    .all()
                ):
                    return [{"role": m.role, "content": m.content} for m in messages]

                else:
                    LOG.error(
                        f"Chat history not found with task_id: {task_id}"
                    )
                    raise NotFoundError("Chat history not found")
        except SQLAlchemyError as e:
            LOG.error(f"SQLAlchemy error while getting chat history: {e}")
            raise
        except NotFoundError as e:
            raise
        except Exception as e:
            LOG.error(f"Unexpected error while getting chat history: {e}")
            raise