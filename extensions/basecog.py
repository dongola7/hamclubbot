import discord
import os

class Cog(discord.Cog):
    """Implements a base class providing common functionality for cogs"""

    def __init__(self, bot: discord.Bot, config_name: str | None = None):
        self.__bot = bot
        if config_name:
            self.__config = bot.config[config_name]
        else:
            self.__config = dict()
        
        self.__embed_config = bot.config['embeds']

    @property
    def bot(self) -> discord.Bot:
        return self.__bot
    
    @property
    def config(self) -> dict:
        return self.__config
    
    def _embed(self, title: str | None = None, description: str | None = None, footer: str | None = None) -> discord.Embed:
        """Creates and returns an embed with consistent formatting"""
        color = discord.Color.blue()
        if 'color' in self.__embed_config:
            color = int(self.__embed_config['color'], 0)
        
        embed = discord.Embed(
            title=title, description=description,
            color=color,
            thumbnail = self.__embed_config.get('thumbnail', None)
        )
        
        if footer:
            embed.set_footer(text=footer)
 
        return embed
