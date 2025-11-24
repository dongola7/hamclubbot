# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

"""Implements derived classes for discord.Bot and discord.Cog to provide common functionality"""

import time
import logging

import discord
import discord.ext.tasks

logger = logging.getLogger(__name__)

class SimpleBot(discord.Bot):
    """Common base class for discord bots providing some standard functionality"""
    class CommandStats:
        """Stores statistics about a command hosted by the bot"""
        def __init__(self, command: str):
            self.__received = 0
            self.__completed = 0
            self.__errors = 0
            self.__command = command

        def __str__(self) -> str:
            return f"cmdstats command={self.__command} received={self.__received} \
completed={self.__completed} errors={self.__errors}"

        def incr_completed(self):
            """Increments the number of completed calls to this command"""
            self.__completed += 1

        def incr_received(self):
            """Increments the number of received calls to this command"""
            self.__received += 1

        def incr_errors(self):
            """Increments the number of calls to this command resulting in an error"""
            self.__errors += 1

    def __init__(self, config: dict | None = None, **kwargs):
        super().__init__(**kwargs)

        # Record the time the bot started
        self.__start_time = time.time()
        self.__config = config if config else {}
        self.owner_id = self.config.get('ownerId', None)

        self.__command_stats = dict[str, SimpleBot.CommandStats]()

    async def on_ready(self):
        """Called once the bot is ready (connected to discord, caches primed, etc)"""
        self.log_command_stats.start()
        logger.info("Username: %s", self.user)
        logger.info("Servers: %d", len(self.guilds))
        logger.info("bot ready...")

    async def on_application_command(self, ctx: discord.ApplicationContext):
        """Called when an application slash command is received"""
        self.__get_command_stats(str(ctx.command)).incr_received()

    async def on_application_command_completion(self, ctx: discord.ApplicationContext):
        """Called when an application slash command completes successfully"""
        self.__get_command_stats(str(ctx.command)).incr_completed()

    async def on_application_command_error(self, context: discord.ApplicationContext,
        exception: discord.DiscordException):
        """Called when an unhandled error occurs while processing a slash command"""
        self.__get_command_stats(str(context.command)).incr_errors()
        logger.error("error while processing command '%s': %s", context.command, exception,
            exc_info=True)

    @discord.ext.tasks.loop(minutes=5)
    async def log_command_stats(self):
        """Called periodically to log statistics on commands called"""
        for stats in self.__command_stats.values():
            logger.info(stats)

    def __get_command_stats(self, command: str):
        if command in self.__command_stats:
            stats = self.__command_stats[command]
        else:
            stats = self.__command_stats[command] = SimpleBot.CommandStats(command)
        return stats

    async def on_unknown_application_command(self, interaction: discord.Interaction):
        """Called when an unknown application command is received"""
        logger.error("received unknown application command: %s", interaction)

    @property
    def config(self) -> dict:
        """Returns the configuration (from file) for the bot"""
        return self.__config

    @property
    def uptime(self) -> float:
        """Returns uptime for the bot in seconds"""
        return time.time() - self.__start_time

class SimpleCog(discord.Cog):
    """Implements a base class providing common functionality for cogs"""

    def __init__(self, bot: SimpleBot, config_name: str | None = None):
        super().__init__()

        self.__bot = bot
        if config_name and (config_name in bot.config):
            self.__config = bot.config[config_name]
        else:
            self.__config = {}

        self.__embed_config = bot.config['embeds']

    @property
    def bot(self) -> SimpleBot:
        """Returns the bot hosting this cog"""
        return self.__bot

    @property
    def config(self) -> dict:
        """Returns the dictionary containing the cogs configuration from the config file"""
        return self.__config

    def _embed(self, title: str | None = None, description: str | None = None,
        footer: str | None = None) -> discord.Embed:
        """Creates and returns an embed with consistent formatting"""
        color = self.__embed_config.get('color', discord.Color.blue())

        embed = discord.Embed(
            title=title, description=description,
            color=color
        )

        if footer:
            embed.set_footer(text=footer)

        return embed
