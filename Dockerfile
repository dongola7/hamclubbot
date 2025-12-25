FROM python:3.13-slim AS build

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip \
    && pip install --user .

FROM python:3.13-slim AS prod

ARG USER=hamclubbot

WORKDIR /app

# Copy packages from the build stage
COPY --from=build /root/.local /home/${USER}/.local

# Install system dependencies (temporary until 2.7.0 of pycord)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create the user and set directory permissions
RUN useradd ${USER}
RUN chown -R ${USER}:${USER} /home/${USER} \
    && chown -R ${USER}:${USER} /app

# Run as the new user, not root
USER ${USER}

ENV BOT_CONFIG=/app/config.yaml
ENV PATH=/home/${USER}/.local/bin:$PATH

CMD exec hamclubbot --config "${BOT_CONFIG}"
