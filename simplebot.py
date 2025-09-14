import discord
import time
import datetime
import logging

logger = logging.getLogger(__name__)

class SimpleBot(discord.Bot):
    """Implements a base class providing some commmon functionality for bots"""
    def __init__(self, config: dict | None = None):
        super().__init__()

        # Record the time the bot started
        self.__start_time = time.time()
        self.__config = config if config else dict()
        self.owner_id = self.config.get('ownerId', None)
   
    async def on_ready(self):
        logger.info(f"Username: {self.user}")
        logger.info(f"Servers: {len(self.guilds)}")
        logger.info("bot ready...")
    
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
        if config_name:
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
            color=color,
            thumbnail = self.__embed_config.get('thumbnail', None)
        )
        
        if footer:
            embed.set_footer(text=footer)
 
        return embed
