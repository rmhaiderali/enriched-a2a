import os
import sys

sys.path.append(os.path.dirname(next((p for p in sys.path if p.endswith(".venv")))))

from main import Agent
from sdks import Pydantic, OpenAI
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

port = 4403

general_conversation_skill = AgentSkill(
    id="general_conversation",
    name="General Conversational Intelligence",
    description="Engages in natural conversation, answers general knowledge questions, provides explanations, and assists with reasoning across diverse topics.",
    tags=[
        "general",
        "conversation",
        "knowledge",
        "language model",
        "reasoning",
        "chat",
    ],
    examples=[
        "What's the capital of France?",
        "Explain how photosynthesis works.",
        "Can you help me write a poem?",
        "What's the meaning of life?",
        "Who won the World Cup in 2018?",
        "Summarize the theory of relativity.",
        "Tell me a joke.",
        "What are black holes?",
    ],
)

card = AgentCard(
    name="General-Purpose Language Agent",
    description="A versatile conversational agent capable of answering questions, explaining concepts, reasoning, and engaging in natural language dialogue across a broad range of topics.",
    url=f"http://localhost:{port}",
    version="1.0.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[general_conversation_skill],
)

agent = Agent(
    sdk=OpenAI,
    # model="gpt-4o-mini",
    # model="anthropic/claude-sonnet-4",
    model="google/gemini-2.0-flash-001",
    #
    # sdk=Pydantic,
    # model="gpt-4o-mini",
    #
    card=card,
    system_prompt="You are a general-purpose conversational agent.",
)

agent.run(port)
