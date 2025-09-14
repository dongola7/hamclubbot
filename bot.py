#!python3

import dotenv
import os
import discord
import logging
import json
import time

# Create logger
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)-8s %(name)s : %(message)s")
logger = logging.getLogger("simple-bot")

# Load config file
CONFIG_PATH = os.getenv("BOT_CONFIG", "./config.json")
try:
    with open(CONFIG_PATH, "r") as config_stream:
        logger.info(f'Loading config from {CONFIG_PATH}')
        config = json.load(config_stream)
        logger.info("successfully loaded config")
except FileNotFoundError:
    logger.error(f"Config file not found at {CONFIG_PATH}")
    raise SystemExit(1)
except Exception as ex:
    logger.error(f"Failed to load config from {CONFIG_PATH}: {ex}")
    raise SystemExit(1)

# Create the bot instance
bot = discord.Bot()
bot.start_time = time.time()
bot.config = config

# Load extensions
bot.load_extension("extensions.conditions")

@bot.event
async def on_ready():
    logger.info(f"Username: {bot.user}")
    logger.info(f"Servers: {len(bot.guilds)}")
    logger.info("bot ready...")

bot.run(config['discordToken'])