# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

FROM base AS deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM base AS runtime
RUN useradd --create-home --uid 10002 agentuser
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY rca_agent/ ./rca_agent/
USER agentuser
EXPOSE 8080
CMD ["uvicorn", "rca_agent.app:app", "--host", "0.0.0.0", "--port", "8080"]
