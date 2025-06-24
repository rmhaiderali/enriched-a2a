import os
import sys

sys.path.append(os.path.dirname(next((p for p in sys.path if p.endswith(".venv")))))

from main import Agent
from llms import Pydantic_LLM
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from pydantic_ai.tools import Tool

port = 4401

get_location_by_ip_skill = AgentSkill(
    id="get_location_by_ip",
    name="Get Location by IP Address",
    description="Retrieves geographical location information (city, country, coordinates, etc.) for a given IP address.",
    tags=["location", "ip address", "geography", "network"],
    examples=[
        "What's the location of 8.8.8.8?",
        "Where is 192.168.1.1 located?",
        "Can you find the geographical data for IP 203.0.113.45?",
        "Tell me the city and country for 172.217.10.14.",
        "What's the geographic info for this IP: 1.1.1.1?",
        "Location of 104.26.2.78",
        "Find details for 13.52.222.181",
        "IP address 93.184.216.34, what's its location?",
    ],
)

card = AgentCard(
    name="IP Location Finder Agent",
    description="An agent that can find geographical location details for IP addresses using an external lookup service.",
    url=f"http://localhost:{port}",
    version="1.0.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[get_location_by_ip_skill],
)

import httpx
import ipaddress


async def get_location_by_ip(ip: str) -> dict:
    """Get location information from an IP address string."""
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise ValueError(f"Invalid IP address: {ip}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://ipleak.net/json/{ip}")
        response.raise_for_status()
        return response.json()


agent = Agent(
    llm=Pydantic_LLM,
    card=card,
    system_prompt="You are a helpful assistant that can answer questions and provide information based on the tools available.",
    tools=[Tool(get_location_by_ip)],
)

agent.run(port)
