#!python3

import os
import simplebot
import logging
import yaml

# Create logger
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)-8s %(name)s : %(message)s")
logger = logging.getLogger("simple-bot")

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
bot.load_extension("extensions.conditions")
bot.load_extension("extensions.clubinfo")
bot.load_extension("extensions.about")

@bot.event
async def on_ready():
    logger.info(f"Username: {bot.user}")
    logger.info(f"Servers: {len(bot.guilds)}")
    logger.info("bot ready...")

bot.run(config['discordToken'])