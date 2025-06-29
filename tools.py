import httpx
from uuid import uuid4
from a2a.client import A2AClient
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
    MessageSendConfiguration,
    JSONRPCErrorResponse,
    Message,
)


async def discover_agents(query: str) -> list:
    """
    Discover agents based on a query string.

    Args:
        query (str): The query string to search for agents.

    Returns:
        list: A list of agent cards that match the query.
    """
    # TODO: Implement actual agent discovery logic.
    return [
        {
            "capabilities": {"streaming": False},
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
            "description": "A simple agent that echoes back any message it receives. Useful for testing basic communication.",
            "name": "Echo Agent",
            "skills": [
                {
                    "description": "Repeats the user's input message exactly as it was received.",
                    "examples": ["hello world", "hi"],
                    "id": "echo",
                    "name": "Echo Input",
                    "tags": ["echo", "utility", "test", "simple"],
                }
            ],
            "url": "http://localhost:4400",
            "version": "1.0.0",
        },
        {
            "capabilities": {"streaming": False},
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
            "description": "An agent that can find geographical location details for IP addresses and resolve domains to IP addresses using an external lookup service.",
            "name": "IP & Domain Network Agent",
            "skills": [
                {
                    "description": "Retrieves geographical location information (city, country, coordinates, etc.) for a given IP address.",
                    "examples": [
                        "What's the location of 8.8.8.8?",
                        "Where is 192.168.1.1 located?",
                        "Can you find the geographical data for IP 203.0.113.45?",
                        "Tell me the city and country for 172.217.10.14.",
                        "What's the geographic info for this IP: 1.1.1.1?",
                        "Location of 104.26.2.78",
                        "Find details for 13.52.222.181",
                        "IP address 93.184.216.34, what's its location?",
                    ],
                    "id": "get_location_by_ip",
                    "name": "Get Location by IP Address",
                    "tags": ["location", "ip address", "geography", "network"],
                },
                {
                    "description": "Retrieves IP addresses associated with a given domain name.",
                    "examples": [
                        "What are the IPs for google.com?",
                        "Get IP addresses for example.com",
                        "Which IPs does openai.com resolve to?",
                        "Find all IPs linked to wikipedia.org",
                        "Show me the IP addresses for github.com",
                    ],
                    "id": "get_ips_by_domain",
                    "name": "Get IPs by Domain",
                    "tags": ["dns", "domain", "ip address", "network"],
                },
            ],
            "url": "http://localhost:4401",
            "version": "1.0.0",
        },
    ]


async def call_agent(
    url: str, prompt: str, context_id: str | None = None, task_id: str | None = None
) -> dict:
    """
    Call an agent with a prompt and optional context or task ID.

    Args:
        url (str): The URL of the agent to call (e.g. http://localhost:9999).
        prompt (str): The prompt to send to the agent.
        context_id (str | None): Optional context ID for the agent.
        task_id (str | None): Optional task ID for the agent.

    Returns:
        dict: The response from the agent.
    """
    async with httpx.AsyncClient(timeout=30) as httpx_client:
        client = A2AClient(httpx_client=httpx_client, url=url)

        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    "role": "user",
                    "messageId": str(uuid4()),
                    "parts": [{"kind": "text", "text": prompt}],
                    "contextId": context_id,
                    "taskId": task_id,
                },
                configuration=MessageSendConfiguration(
                    acceptedOutputModes=["text"], blocking=False
                ),
            ),
        )

        response = None
        try:
            response = await client.send_message(request)
        except Exception as e:
            return {"error": "Failed to call agent"}

        if isinstance(response.root, JSONRPCErrorResponse):
            return response.root.error
        elif isinstance(response.root.result, Message):
            return response.root.result
        else:
            # TODO: Implement task handling
            return {"error": "server returned task. which is not supported yet"}
