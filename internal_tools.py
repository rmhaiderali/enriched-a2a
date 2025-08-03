import os
import sys
import json
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

    example_agents = []
    example_agents_dir = f"{sys.path[0]}/example_agents"

    for agent_dir in os.listdir(example_agents_dir):
        try:
            with open(f"{example_agents_dir}/{agent_dir}/metadata.json", "r") as f:
                card = json.load(f).get("card")
                if card:
                    example_agents.append(card)

        except Exception as e:
            continue

    return example_agents


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
