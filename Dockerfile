FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN uv sync --locked

COPY . /app/

ENV PORT=3200

EXPOSE 3200

CMD ["uv", "run", "start.py", "/app/example_agents/ip_location_finder"]

# docker build -t a2a-0-X-X .
