import sys
import json
from main import Agent
from sdks import Echo, Pydantic, OpenAI
from a2a.types import AgentCard

if len(sys.argv) == 1:
    print("Usage: uv run start.py path/to/agent/dir")
    sys.exit(1)

dir = sys.argv[1]

sdks = {"echo": Echo, "pydantic": Pydantic, "openai": OpenAI}

with open(f"{dir}/metadata.json", "r") as file:

    metadata = json.load(file)

    card = metadata.get("card")
    if not card:
        print("No card found in metadata.json")
        sys.exit(1)

    metadata["card"] = AgentCard(**card)

    sdk = metadata.get("sdk")
    if not sdk:
        print("No sdk specified in metadata.json")
        sys.exit(1)

    if sdk not in sdks:
        print(f"Unsupported SDK: {sdk}. Supported SDKs are: {', '.join(sdks.keys())}")
        sys.exit(1)

    metadata["sdk"] = sdks[sdk]

    try:
        sys.path.append(dir)
        from tools import tools

        metadata["tools"] = tools
        sys.path.remove(dir)
    except Exception as e:
        print(f"Error loading tools: {e}")
        pass

    port = metadata.pop("port", 3200)
    agent = Agent(**metadata)
    agent.run(port)
