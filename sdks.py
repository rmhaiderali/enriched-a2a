import os
import json
from abc import abstractmethod
from dotenv import load_dotenv
from pydantic_ai.tools import Tool
from rich.console import Console
from rich.traceback import Traceback

load_dotenv()
console = Console()


class SDK:
    @abstractmethod
    def __init__(self, model: str, system_prompt: str, tools: list[Tool]) -> None:
        """Initialize the LLM with a system prompt.

        Args:
            system_prompt (str): The system prompt to guide the LLM's behavior.
        """

    @abstractmethod
    async def run(self, message: str, context_id: str) -> str:
        """Run the LLM with a given message and context ID.

        Args:
            message (str): The input message to process.
            context_id (str): The context ID for the conversation.

        Returns:
            str: The output generated by the LLM.
        """


class Echo(SDK):
    def __init__(self, model: str, system_prompt: str, tools: list[Tool]) -> None:
        """"""

    async def run(self, message: str, context_id: str) -> str:
        return f"echo: {message}"


class Pydantic(SDK):
    def __init__(self, model: str, system_prompt: str, tools: list[Tool]) -> None:
        from pydantic_ai import Agent

        self.agent = Agent(model, system_prompt=system_prompt)
        self.contexts = {}

        for tool in tools:
            self.agent._register_tool(tool)

    async def run(self, message: str, context_id: str) -> str:
        if not isinstance(self.contexts.get(context_id), list):
            self.contexts[context_id] = []

        result = None
        try:
            result = await self.agent.run(
                message, message_history=self.contexts[context_id]
            )
        except Exception as e:
            console.print(Traceback())

        if result:
            self.contexts[context_id].extend(result.new_messages())

        return result.output if result else "Error while calling LLM"


class OpenAI(SDK):
    def __init__(self, model: str, system_prompt: str, tools: list[Tool]) -> None:
        from openai import OpenAI as Agent

        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.agent = Agent(base_url=os.getenv("OPENAI_API_BASE"))
        self.contexts = {}

    async def run(self, message: str, context_id: str) -> str:
        if not isinstance(self.contexts.get(context_id), list):
            self.contexts[context_id] = []

        self.contexts[context_id].append(
            {"role": "system", "content": self.system_prompt}
        )
        self.contexts[context_id].append({"role": "user", "content": message})

        result = None
        try:
            while True:
                result = self.agent.chat.completions.create(
                    model=self.model,
                    messages=self.contexts[context_id],
                    tools=[
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.function_schema.json_schema,
                            },
                        }
                        for tool in self.tools
                    ],
                )

                self.contexts[context_id].append(result.choices[0].message)

                if not result.choices[0].message.tool_calls:
                    break

                for tool_call in result.choices[0].message.tool_calls:
                    tool = next(
                        (t for t in self.tools if t.name == tool_call.function.name),
                    )

                    tool_result = await tool.function(
                        **json.loads(tool_call.function.arguments)
                    )

                    self.contexts[context_id].append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result),
                        }
                    )
        except Exception as e:
            console.print(Traceback())

        output = (
            result.choices[0].message.content if result else "Error while calling LLM"
        )

        return output
