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