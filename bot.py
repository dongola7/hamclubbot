#!python3

import os
import extensions.util.simplebot as simplebot
import logging
import yaml
import discord

# Create logger
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)-8s %(name)s : %(message)s")
logger = logging.getLogger("bot")

# Load config file
CONFIG_PATH = os.getenv("BOT_CONFIG", "./config.yaml")
try:
    with open(CONFIG_PATH, "r") as config_stream:
        logger.info(f'Loading config from {CONFIG_PATH}')
        config = yaml.safe_load(config_stream)
        logger.info("successfully loaded config")
except FileNotFoundError:
    logger.error(f"Config file not found at {CONFIG_PATH}")
    raise SystemExit(1)
except Exception as ex:
    logger.error(f"Failed to load config from {CONFIG_PATH}: {ex}")
    raise SystemExit(1)

# Create the bot instance
bot = simplebot.SimpleBot(config)

# Load extensions
extensions = [
    "extensions.conditions",
    "extensions.clubinfo",
    "extensions.about",
]

for extension in extensions:
    try:
        bot.load_extension(extension)
        logger.info(f"loaded extension {extension}")
    except Exception as ex:
        logger.error(f"Failed to load extension {extension}: {ex}")
logger.info("completed loading extensions")

# Start the bot
try:
    logger.info("Starting bot...")
    bot.run(config['discordToken'])
except discord.LoginFailure as ex:
    logger.critical(f"Failed to authenticate to discord: {ex}")
    raise SystemExit("Error: Failed to authenticate with discord")
except discord.ConnectionClosed as ex:
    logger.critical(f"Gateway connection to discord closed: code={ex.code} reason={ex.reason}")
    raise SystemExit("Error: gateway connection to discord closed")
except ConnectionResetError as ex:
    logger.critical(f"ConnectionResetError: {ex}")
    raise SystemExit(f"ConnectionResetError: {ex}")
except Exception as ex:
    logger.critical(f"Unexpected error: {ex}")
    raise SystemExit(f"Critical unexpected error: {ex}")