FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN apt-get update \
    && apt-get install -y --no-install-recommends libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

ENV BOT_CONFIG=/app/config.yaml

CMD ["python3", "bot.py"]
