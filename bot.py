#!python3

# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

"""Implements a basic discord bot for ham radio clubs"""

import logging
import logging.config
import argparse
import yaml
import discord
from extensions.util import simplebot

# Parse command line arguments
parser = argparse.ArgumentParser(description="Discord bot for use in ham radio club discords")
parser.add_argument("-c", "--config", required=True, help="Config file location")
args = parser.parse_args()

# Load config file
try:
    with open(args.config, "r", encoding="utf-8") as config_stream:
        config = yaml.safe_load(config_stream)
except FileNotFoundError as ex:
    raise SystemExit(f"Config file not found at {args.config}") from ex
except Exception as ex:
    raise SystemExit(f"Failed to load config from {args.config}: {ex}") from ex

# Configure logging if present in config
if 'logging' in config:
    config['logging']['version'] = 1
    config['logging']['incremental'] = False
    config['logging']['disable_existing_loggers'] = False
    logging.config.dictConfig(config['logging'])
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s : %(message)s")

# Create the logger
logger = logging.getLogger("bot")

# Create the bot instance
bot = simplebot.SimpleBot(config)

# Load extensions
extensions = [
    "extensions.conditions",
    "extensions.clubinfo",
    "extensions.about",
    "extensions.pota",
]

for extension in extensions:
    try:
        bot.load_extension(extension)
        logger.info("loaded extension %s", extension)
    except discord.ExtensionError as ex:
        logger.error("Failed to load extension %s: %s", extension, ex)
logger.info("completed loading extensions")

# Start the bot
try:
    logger.info("Starting bot...")
    bot.run(config['discordToken'])
except discord.LoginFailure as ex:
    logger.critical("Failed to authenticate to discord: %s", ex)
    raise SystemExit("Error: Failed to authenticate with discord") from ex
except discord.ConnectionClosed as ex:
    logger.critical("Gateway connection to discord closed: code=%s reason=%s", ex.code, ex.reason)
    raise SystemExit("Error: gateway connection to discord closed") from ex
except ConnectionResetError as ex:
    logger.critical("ConnectionResetError: %s", ex)
    raise SystemExit(f"ConnectionResetError: {ex}") from ex
except Exception as ex:
    logger.critical("Unexpected error: %s", ex)
    raise SystemExit(f"Critical unexpected error: {ex}") from ex
