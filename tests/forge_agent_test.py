import os
import asyncio
import unittest
import functools
from app import ForgeAgent, ForgeDatabase
from app.core import LocalWorkspace
from app.core.models.TaskRequestBody import TaskRequestBody
from app.core.models.StepRequestBody import StepRequestBody
from app.core.models.Status import Status

def async_test(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(*args, **kwargs))
    return wrapper

class TestForgeAgent(unittest.TestCase):
    input = "Test input"
    @classmethod
    def setUpClass(cls):
        database_name = os.getenv("TEST_DATABASE_STRING") or "sqlite:///test.db"
        workspace_name = os.getenv("TEST_AGENT_WORKSPACE") or "./test_workspace"
        cls.db = ForgeDatabase(database_name)
        cls.workspace = LocalWorkspace(workspace_name)
        cls.agent = ForgeAgent(database=cls.db, workspace=cls.workspace, debug_enabled=False)

    def setUp(self):
        # Setup any necessary data before each test
        pass

    def tearDown(self):
        # Clean up after each test
        pass

    @async_test
    async def test_create_task(self):
        task_request = TaskRequestBody(input=self.input)
        task = await self.agent.create_task(task_request)
        self.assertIsNotNone(task)
        self.assertEqual(task.input, self.input)

    @async_test
    async def test_create_step(self):
        task_request = TaskRequestBody(input=self.input)
        task = await self.agent.create_task(task_request)
        task_id = task.task_id
        step_request = StepRequestBody(input=self.input)
        step = await self.agent.create_step(task_id, step_request)
        self.assertIsNotNone(step)
        self.assertEqual(step.input, self.input)

    @async_test
    async def test_update_task(self):
        task_request = TaskRequestBody(input=self.input)
        task = await self.agent.create_task(task_request)
        self.assertEqual(task.input, self.input)
        task_id = task.task_id
        updated_input = "Updated task input"
        await self.agent.db.update_task(task_id)
        updated_task = await self.agent.db.get_task(task_id)
        self.assertNotEqual(updated_task.input, updated_input)

    @async_test
    async def test_update_step(self):
        task_request = TaskRequestBody(input=self.input)
        task = await self.agent.create_task(task_request)
        task_id = task.task_id
        step_request = StepRequestBody(input=self.input)
        step = await self.agent.create_step(task_id, step_request)
        self.assertEqual(step.input, self.input)
        step_id = step.step_id
        updated_input = "Updated step input"
        await self.agent.db.update_step(task_id, step_id)
        updated_step = await self.agent.db.get_step(task_id, step_id)
        self.assertNotEqual(updated_step.input, updated_input)

    @async_test
    async def test_execute_step(self):
        task_request = TaskRequestBody(input=self.input)
        task = await self.agent.create_task(task_request)
        task_id = task.task_id
        step_request = StepRequestBody(input=self.input)
        step = await self.agent.create_step(task_id, step_request)
        self.assertEqual(step.input, self.input)
        step_id = step.step_id
        updated_input = "Updated step input"
        await self.agent.db.update_step(task_id, step_id)
        updated_step = await self.agent.db.get_step(task_id, step_id)
        self.assertNotEqual(updated_step.input, updated_input)
        stepExecution = await self.agent.execute_step(task_id, step_request)
        self.assertIsNotNone(stepExecution)
        self.assertEqual(stepExecution.status, Status.completed)

    @async_test
    async def test_list_non_completed_steps(self):
        task_id = "test_task_id"
        response = await self.agent.list_non_completed_steps(task_id)
        self.assertIsInstance(response, dict)
        self.assertIn("steps", response)

    # Additional tests can be added here for delete operations or other functionalities

if __name__ == "__main__":
    asyncio.run(unittest.main())
# if __name__ == "__main__":
#     unittest.main(testRunner=AsyncioTestRunner)
