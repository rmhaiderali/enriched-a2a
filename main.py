import uvicorn
from a2a.types import AgentCard
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.utils import new_agent_text_message
from pydantic_ai.tools import Tool
from llms import LLM


class Executor(AgentExecutor):
    def __init__(self, llm: LLM):
        self.llm = llm

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        input = context.get_user_input()
        context_id = context.message.contextId
        task_id = context.message.taskId

        output = await self.llm.run(input, context_id)

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
        llm: LLM,
        card: AgentCard,
        extended_card: AgentCard | None = None,
        system_prompt: str = "",
        tools: list[Tool] = [],
    ):
        self.card = card
        self.extended_card = extended_card
        for tool in tools:
            if not isinstance(tool, Tool):
                raise TypeError(f"{tool} is not an instance of pydantic ai tool")
        self.llm = llm(system_prompt=system_prompt, tools=tools)

        if not isinstance(self.card, AgentCard):
            raise TypeError("card must be an instance of AgentCard")

        if not isinstance(self.extended_card, AgentCard | None):
            raise TypeError("extended_card must be an instance of AgentCard")

    def run(self, port: int = 9999):
        if not isinstance(port, int) or (port < 1 and port > 65535):
            raise ValueError("port must be an integer between 1 and 65535")

        request_handler = DefaultRequestHandler(
            agent_executor=Executor(llm=self.llm),
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=self.card,
            extended_agent_card=self.extended_card,
            http_handler=request_handler,
        )

        uvicorn.run(server.build(), port=port)
