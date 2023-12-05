import os

from app.agent import ForgeAgent
from app.core import LocalWorkspace
from .db import ForgeDatabase

# Get the database string from environment variables
database_name = os.getenv("DATABASE_STRING")

# Create a LocalWorkspace object using the AGENT_WORKSPACE environment variable
workspace = LocalWorkspace(os.getenv("AGENT_WORKSPACE"))

# Create a ForgeDatabase object with the database name and disable debug mode
database = ForgeDatabase(database_name, debug_enabled=False)

# Create a ForgeAgent object with the database and workspace
agent = ForgeAgent(database=database, workspace=workspace)

# Get the agent's FastAPI app
app = agent.get_agent_app()