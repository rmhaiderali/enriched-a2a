import uvicorn
import inspect
from a2a.types import AgentCard
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.utils import new_agent_text_message
from pydantic_ai.tools import Tool
from sdks import SDK
from internal_tools import discover_agents, call_agent


class Executor(AgentExecutor):
    def __init__(self, agent: SDK):
        self.agent = agent

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        input = context.get_user_input()
        context_id = context.message.contextId
        task_id = context.message.taskId

        output = await self.agent.run(input, context_id)

        await event_queue.enqueue_event(
            new_agent_text_message(output, context_id, task_id)
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        raise Exception("cancel not supported")


class Agent:
    def __init__(
        self,
        sdk: SDK,
        card: AgentCard,
        model: str | None = None,
        extended_card: AgentCard | None = None,
        system_prompt: str = "",
        tools: list[Tool] = [],
    ):
        self.card = card
        self.extended_card = extended_card

        for index, tool in enumerate(tools):
            if not inspect.isfunction(tool):
                raise TypeError(f"Element at index {index} is not a function")
            if tool.__name__ == "<lambda>":
                raise ValueError(
                    f"Element at index {index} is a lambda which is not allowed"
                )
            tools[index] = Tool(tool)

        tools.append(Tool(discover_agents))
        tools.append(Tool(call_agent))

        system_prompt = (
            "You have a tool called 'discover_agents' that can be used to "
            "discover agents for a specific task. It returns a list of agent "
            "cards based on a search query (like google search). You can use "
            "it to find agents that can help you with your task. After getting "
            "agent cards list you can pick a agent (based on agent card which "
            "includes all detiled information about agent including its skills "
            "and capabilities. You have to provide url and a prompt in natural "
            "language to use 'call_agent' tool.\n" + system_prompt
        )

        self.agent = sdk(model=model, system_prompt=system_prompt, tools=tools)

        if not isinstance(self.card, AgentCard):
            raise TypeError("card must be an instance of AgentCard")

        if not isinstance(self.extended_card, AgentCard | None):
            raise TypeError("extended_card must be an instance of AgentCard")

    def run(self, port: int = 9999):
        if not isinstance(port, int) or (port < 1 and port > 65535):
            raise ValueError("port must be an integer between 1 and 65535")

        request_handler = DefaultRequestHandler(
            agent_executor=Executor(agent=self.agent),
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=self.card,
            extended_agent_card=self.extended_card,
            http_handler=request_handler,
        )

        uvicorn.run(server.build(), port=port)
