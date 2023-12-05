from app.core import (
    Agent,
    AgentDB,
    ForgeLogger,
    Workspace,
    PromptEngine,
    chat_completion_request,
    convert_to_step
)
from app.core.models.StepModel import StepModel
from app.core.models.StepRequestBody import StepRequestBody
from app.core.models.TaskRequestBody import TaskRequestBody
from app.core.models.Task import Task
from app.core.models.Step import Step
from app.core.models.Status import Status
import json
from pprint import pprint
from datetime import datetime
import subprocess
import os

LOG = ForgeLogger(__name__)
class ForgeAgent(Agent):
    constraints, resources, commands, best_practices = None, None, None, None
    def __init__(self, database: AgentDB, workspace: Workspace, debug_enabled: bool = True):
        # turns on debug mode | helpful for debugging what's going on with your object models
        self.debug_enabled = debug_enabled
        database.debug_enabled = self.debug_enabled
        super().__init__(database, workspace)
    def set_prompts(self, input):
        #TODO move to a config file
        self.constraints = [
            "Exclusively use the commands/abilities listed below.",
            "You can only act proactively, and are unable to start background jobs or set up webhooks for yourself. Take this into account when planning your actions.",
            "You are unable to interact with physical objects. If this is absolutely necessary to fulfill a task or objective or to complete a step, you must ask the user to do it for you. If the user refuses this, and there is no other way to achieve your goals, you must terminate to avoid wasting time and energy.",
            "Do not use offensive or inappropriate language when greeting users.",
            "Do not ignore or dismiss greetings from users.",
            "Do not respond to greetings with overly formal or rigid language."
        ]
        self.resources = [
            "Internet access for searches and information gathering.",
            "The ability to read and write files.",
            "You are a Large Language Model, trained on millions of pages of text, including a lot of factual knowledge. Make use of this factual knowledge to avoid unnecessary gathering of information."
        ]
        self.actions = [
            "play_music: Takes input and launch the configured music provider of choice and plays the desired request from the user. Params: (code: list). CLI invokation of itunes: /mnt/c/Windows/System32/cmd.exe /c start itunes",
            "execute_python_code: Executes the given Python code inside a single-use Docker container with access to your workspace folder. Params: (code: string)",
            "execute_python_file: Execute an existing Python file inside a single-use Docker container with access to your workspace folder. Params: (filename: string, args: array)",
            "execute_shell: Execute a Shell Command, non-interactive commands only. Params: (command_line: string)",
            "execute_shell_popen: Execute a Shell Command, non-interactive commands only. Params: (command_line: string)",
            "list_folder: List the items in a folder. Params: (folder: string)",
            "open_file: Open a file for editing or continued viewing; create it if it does not exist yet. Note: if you only need to read or write a file once, use `write_to_file` instead.. Params: (file_path: string)",
            "open_folder: Open a folder to keep track of its content. Params: (path: string)",
            "read_file: Read an existing file. Params: (filename: string)",
            "write_file: Write a file, creating it if necessary. If the file exists, it is overwritten.. Params: (filename: string, contents: string)",
            "ask_user: If you need more details or information regarding the given goals, you can ask the user for input. Params: (question: string)",
            "web_search: Searches the web. Params: (query: string)",
            "read_webpage: Read a webpage, and extract specific information from it if a question is specified. If you are looking to extract specific information from the webpage, you should specify a question.. Params: (url: string, question: string)",
            "finish: Use this to shut down once you have completed your task, or when there are insurmountable problems that make it impossible for you to finish your task. Params: (reason: string)"
        ]
        self.best_practices = [
            "Continuously review and analyze your actions to ensure you are performing to the best of your abilities.",
            "Constructively self-criticize your big-picture behavior constantly.",
            "Reflect on past decisions and strategies to refine your approach.",
            "Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps.",
            "Only make use of your information gathering abilities to find information that you don't yet have knowledge of.",
            "Respond to greetings in a friendly and jovial manner, while maintaining the utmost respect for the user's communication style.",
            "Avail yourself to respond at all times to provide an immediate greeting to any user.",
            "Maintain a light and pleasant tone during interactions.",
            "Base your responses on the tone, language and intensity of the user's greeting."
        ]
        prompt_engine = PromptEngine("jaida", self.debug_enabled)
        agent_prompt = prompt_engine.load_prompt("agent-format", task=input, constraints=self.constraints, resources=self.resources, best_practices=self.best_practices, actions=self.actions)
        system_prompt = prompt_engine.load_prompt("system-format")
        combined_prompt = agent_prompt + system_prompt
        #print(combined_prompt)
        return combined_prompt
    async def create_step(self, task_id, step_request, is_last=False) -> Step:
        return await self.db.create_step(task_id=task_id, input=step_request, is_last=is_last)

    async def create_task(self, task_request: TaskRequestBody) -> Task:
        # based on the task input, the agent personality will be created to do the specific task however the agent profile should remain somewhat consistent, so we create an artifact out of the j2 template system here that the execute_step will continue to run and run as long as it gets called again and again until it completes it's task
        prompt = self.set_prompts(task_request.input)
        persona = await self.create_persona(prompt)
        brain = json.loads(persona['choices'][0]['message']['content'])
        print(brain)
        plan = brain['thoughts']['planning']
        steps_info = plan['steps']
        output = {
            "steps_created": [],
        }
        task = await super().create_task(task_request)
        task_id = task.task_id
        chatbot_response = brain['thoughts']['speak']
        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": task_request.input
            },
            {
                "role": "assistant",
                "content": chatbot_response
            }
        ]
        await self.db.add_chat_history(task_id, messages)
        # Iterate through the steps_info and create steps in the database
        for step_info in steps_info:
            # Call the create_step function from the db class for each step
            step = await self.create_step(task_id,task_request,(step_info == steps_info[-1]))
            output["steps_created"].append({"step_id": step.step_id, "output": step.input})
            # Assuming there's a method to associate the step with the task in the application
        task.additional_output = output
        task.output = chatbot_response

        return task
    async def execute_step(self, task_id: str, request: StepRequestBody) -> Step:
        # Get the list of non-completed steps
        steps = (await self.list_non_completed_steps(task_id))['steps']
        current_time = datetime.now()
        if steps:
            # Execute the first non-completed step
            for step in steps:
                if(len(steps) > 0):
                    if step.status != Status.completed:

                        messages = await self.db.get_chat_history(task_id)
                        #llm = self.call_llm()
                        #messages.append({"role": "system", "content": "Make sure to respond only with the correct json format."})
                        messages.append({"role": "user", "content": request.input})
                        LOG.debug(f"messages: {messages}")
                        message = await self.send_message(messages)
                        brain = json.loads(message)
                        LOG.debug(f"brain: {brain}")
                        step.output = brain['thoughts']['speak']
                        additional_output = await self.update_additional_output(step.task_id, step.step_id)
                        # Update the step in the database
                        step = await self.db.update_step(
                            task_id,
                            step.step_id,
                            Status.completed.value,
                            step.output,
                            step.additional_input,
                            additional_output
                        )
                        planning_steps = brain['thoughts']['planning']['steps']
                        if(len(planning_steps) > 0):
                            for new_step in planning_steps:
                                LOG.debug(f"planning step: {new_step}")
                                planning_input = StepRequestBody(input=new_step)
                                await self.create_step(task_id,planning_input,(new_step == planning_steps[-1]))
                        # update task if this is the last step
                        if step.is_last:
                            await self.db.update_task(task_id, Status.completed.value, step.output, step.additional_input, additional_output)
                            #step = await self.create_step(task_id,task_request,(step_info == steps_info[-1]))
                            #await self.db.update_task(task_id, Status.in_progress.value, step.output, step.additional_input, additional_output)
                        await self.db.add_chat_message(task_id, "user", request.input)
                        await self.db.add_chat_message(task_id, "assistant", step.output)
                        return step
            # Handle the case when there are no non-completed steps
        else:
            step = Step(task_id=task_id, step_id="null", status=Status.completed.value, output="there are no more steps to execute", created_at=current_time, modified_at=current_time, is_last=True, name="no more steps to execute", additional_output=await self.update_additional_output(task_id))
            if step.is_last:
                await self.db.update_task(task_id, Status.completed.value)
            return step
    async def list_non_completed_steps(self, task_id: str):
        steps_list = await self.list_steps(task_id)
        non_completed_steps = [
            step for step in steps_list.steps if step.status != Status.completed
        ]
        if not non_completed_steps:
            return {"message": "No more steps to execute", "steps": []}

        return {"steps": non_completed_steps}

    async def update_additional_output(self, task_id, current_step_id=None):
        task = await self.list_steps(task_id)
        additional_output = {
            "completed_steps": [],
            "remaining_steps": []
        }

        for step in task.steps:
            if step.status == Status.completed or step.is_last:
                additional_output["completed_steps"].append(step.step_id)
            else:
                additional_output["remaining_steps"].append(step.step_id)

        return additional_output

    async def create_persona(self,prompt):
        chat_completion_kwargs = {
            "messages": [{"role": "system", "content": prompt}],
            "model": "gpt-3.5-turbo-1106",
            "temperature": 0,
            "response_format": {"type": "json_object"}
        }
        persona = await chat_completion_request(**chat_completion_kwargs)
        LOG.debug(f"Persona: {persona}")
        return persona
    async def send_message(self, messages):
        chat_completion_kwargs = {
            "messages": messages,
            "model": "gpt-3.5-turbo-1106",
            "temperature": 0,
            "response_format": {"type": "json_object"}
        }
        message = await chat_completion_request(**chat_completion_kwargs)
        LOG.debug(f"Message: {message}")
        return message['choices'][0]['message']['content']