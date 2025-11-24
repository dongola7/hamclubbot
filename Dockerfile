FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY src .
COPY pyproject.toml .
COPY LICENSE .

RUN pip install --upgrade pip \
    && pip install .

ENV BOT_CONFIG=/app/config.yaml

CMD exec hamclubbot --config ${BOT_CONFIG}
