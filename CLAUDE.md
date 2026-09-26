# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install system dependencies (macOS)
brew bundle

# Set up development environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run the bot
DISCORD_TOKEN=<token> hamclubbot --config ./config/config.yaml

# Run tests
pytest

# Run a single test file
pytest tests/path/to/test_file.py

# Lint
pylint src/

# Build Docker image
docker build -t hamclubbot .

# Run via Docker (requires config at ~/config.yaml)
docker run -e DISCORD_TOKEN=<token> -v $(HOME)/config.yaml:/app/config.yaml hamclubbot

# Generate config from template
cp ./config/config.yaml.tmpl ./config/config.yaml
```

## Architecture

This is a Discord bot for amateur radio clubs built with [Pycord](https://docs.pycord.dev/) (Python 3.13+). The bot uses the Discord.py **Cog** extension system for modularity.

### Extension/Cog Pattern

All bot functionality lives in `src/hamclubbot/extensions/`. Each extension is a `SimpleCog` subclass that is auto-loaded by `__main__.py`. Configuration for each extension lives under a matching key in `config.yaml`.

`SimpleCog` (in `extensions/util/simplebot.py`) provides:
- Access to the section of the config file relevant to the cog
- A `_embed()` helper for creating consistently styled Discord embeds

`SimpleBot` (also in `simplebot.py`) wraps `discord.Bot` and adds command statistics tracking and periodic logging.

### Utilities

- **`webcache.py`**: In-memory HTTP response cache with configurable TTL (default 15 min). Caches raw content plus an optional "extra" value (e.g., a pre-converted PNG alongside raw SVG).
- **`persistentstore.py`**: Per-guild SQLite key-value store. Used by `clubinfo.py` to store guild-specific content.
- **`views.py`**: Reusable Discord UI components (currently just a yes/no confirmation view).

### Extensions

| Extension | Slash Commands | External Data |
|-----------|---------------|---------------|
| `conditions.py` | `/cond`, `/muf` | hamqsl.com (solar), prop.kc2g.com (MUF map) |
| `clubinfo.py` | `/club`, `/manage_club` | Guild SQLite DB |
| `pota.py` | `/pota activations`, `/pota callstats` | pota.app API |
| `about.py` | `/about` | None |

### Config Structure

The Discord token is read from the `DISCORD_TOKEN` environment variable, not the config file.

`config.yaml` (copied from `config/config.yaml.tmpl` and filled in):
```yaml
ownerId: <discord-user-id>
clubInfo:
  database_path: ./clubinfo.db
embeds:
  color: 0x2ecc71
```

### Linting

Pylint is configured via `pylintrc`. Key rules: max line length 100, Python 3.13 target. Run `pylint src/` before committing.
