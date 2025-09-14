# Description

A basic discord bot created using [discord.py](https://discordpy-reborn.readthedocs.io/)

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
op inject -i config.yaml.tmpl -o config.yaml
```
