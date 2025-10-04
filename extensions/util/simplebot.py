# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

import discord
import discord.ext.tasks
import time
import datetime
import logging

logger = logging.getLogger(__name__)

class SimpleBot(discord.Bot):
    class CommandStats:
        def __init__(self, command: str):
            self.__received = 0
            self.__completed = 0
            self.__errors = 0
            self.__command = command

        def __str__(self) -> str:
            return f"cmdstats command={self.__command} received={self.__received} completed={self.__completed} errors={self.__errors}"

        def incr_completed(self):
            self.__completed += 1

        def incr_received(self):
            self.__received += 1

        def incr_errors(self):
            self.__errors += 1

    """Implements a base class providing some commmon functionality for bots"""
    def __init__(self, config: dict | None = None, **kwargs):
        super().__init__(**kwargs)

        # Record the time the bot started
        self.__start_time = time.time()
        self.__config = config if config else dict()
        self.owner_id = self.config.get('ownerId', None)

        self.__command_stats = dict[str, SimpleBot.CommandStats]()
   
    async def on_ready(self):
        self.log_command_stats.start()
        logger.info(f"Username: {self.user}")
        logger.info(f"Servers: {len(self.guilds)}")
        logger.info("bot ready...")

    async def on_application_command(self, ctx: discord.ApplicationContext):
        self.__get_command_stats(str(ctx.command)).incr_received()

    async def on_application_command_completion(self, ctx: discord.ApplicationContext):
        self.__get_command_stats(str(ctx.command)).incr_completed()

    async def on_application_command_error(self, context: discord.ApplicationContext, exception: discord.DiscordException):
        self.__get_command_stats(str(context.command)).incr_errors()
        logger.error("error while processing command '%s': %s", context.command, exception, exc_info=True)

    @discord.ext.tasks.loop(minutes=5)
    async def log_command_stats(self):
        for stats in self.__command_stats.values():
            logger.info(stats)

    def __get_command_stats(self, command: str):
        if command in self.__command_stats:
            stats = self.__command_stats[command]
        else:
            stats = self.__command_stats[command] = SimpleBot.CommandStats(command)
        return stats

    async def on_unknown_application_command(self, interaction: discord.Interaction):
        logger.error(f"received unknown application command: {interaction}")

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
            self.__config = dict()
        
        self.__embed_config = bot.config['embeds']

    @property
    def bot(self) -> SimpleBot:
        return self.__bot
    
    @property
    def config(self) -> dict:
        return self.__config
    
    def _embed(self, title: str | None = None, description: str | None = None, footer: str | None = None) -> discord.Embed:
        """Creates and returns an embed with consistent formatting"""
        color = self.__embed_config.get('color', discord.Color.blue())
        
        embed = discord.Embed(
            title=title, description=description,
            color=color
        )
        
        if footer:
            embed.set_footer(text=footer)
 
        return embed
