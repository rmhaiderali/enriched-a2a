import os
import sys

sys.path.append(os.path.dirname(next((p for p in sys.path if p.endswith(".venv")))))

from main import Agent
from llms import Echo
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

port = 4400

echo_skill = AgentSkill(
    id="echo",
    name="Echo Input",
    description="Repeats the user's input message exactly as it was received.",
    tags=["echo", "utility", "test", "simple"],
    examples=["hello world", "hi"],
)

card = AgentCard(
    name="Echo Agent",
    description="A simple agent that echoes back any message it receives. Useful for testing basic communication.",
    url=f"http://localhost:{port}",
    version="1.0.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[echo_skill],
)

agent = Agent(llm=Echo, card=card)

agent.run(port)
