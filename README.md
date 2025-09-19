# Description

A discord bot intended for use in servers for Amateur Radio Clubs. Provides a series of
useful tools for managing the club, looking up weather conditions for radio operation, etc.

The bot is built using the [Pycord](https://pycord.dev) framework.

# Getting Started

```bash
# Install system dependencies (requires Homebrew from https://brew.sh)
brew bundle

# Create and activate a python virtual environment
python3 -m venv local-env
source local-env/bin/activate

# Install required packages
pip install -r requirements.txt

# Generate the config file from 1Password
op inject -i ./config/config.yaml.tmpl -o ./config/config.yaml

# Run the bot
./bot.py --config ./config/config.yaml
```

# Docker Image

You can run the bot directly or build a Docker image using the included Dockerfile
to run the bot. If using a Docker image, the Dockerfile is configured to expect
the configuration to be located in /app/config.yaml. You need to mount the
configuration file accordingly.

For example:

```bash
# Build the docker image and tag it as hamclubbot
docker build -t hamclubbot .

# Run a docker container, exposing $(HOME)/config.yaml as the bot configuration
docker run -v $(HOME)/config.yaml:/app/config.yaml hamclubbot
```