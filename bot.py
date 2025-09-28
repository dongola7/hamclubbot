#!python3

# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

import extensions.util.simplebot as simplebot
import logging
import logging.config
import yaml
import discord
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Discord bot for use in ham radio club discords")
parser.add_argument("-c", "--config", required=True, help="Config file location")
args = parser.parse_args()

# Load config file
try:
    with open(args.config, "r") as config_stream:
        config = yaml.safe_load(config_stream)
except FileNotFoundError:
    raise SystemExit(f"Config file not found at {args.config}")
except Exception as ex:
    raise SystemExit(f"Failed to load config from {args.config}: {ex}")

# Configure logging if present in config
if 'logging' in config:
    config['logging']['version'] = 1
    config['logging']['incremental'] = False
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