# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

FROM base AS deps
# Optional PEM roots for PyPI/pip behind TLS inspection (see app/README.md, app/docker-certs/)
COPY docker-certs/ /tmp/docker-certs/
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && i=0 \
    && for f in /tmp/docker-certs/*.crt /tmp/docker-certs/*.cer /tmp/docker-certs/*.pem; do \
         if [ -f "$f" ] && grep -q "BEGIN CERTIFICATE" "$f" 2>/dev/null; then \
           i=$((i + 1)); cp "$f" "/usr/local/share/ca-certificates/corp-build-$i.crt"; \
         fi; \
       done \
    && update-ca-certificates \
    && rm -rf /tmp/docker-certs \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM base AS runtime
RUN useradd --create-home --uid 10001 appuser
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY demo_app/ ./demo_app/
USER appuser
EXPOSE 8000
CMD ["uvicorn", "demo_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
