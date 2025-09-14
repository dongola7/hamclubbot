import discord
import logging
import simplebot

logger = logging.getLogger(__name__)

class ClubInfo(simplebot.SimpleCog):
    """
    Implements commands providing club information

    This Cog provides a command 'club' for members to request more information about various
    aspects of the club. The Cog uses the Discord autocomplete feature to produce a dynamic
    list of possible queries based on the bots configuration. This allows the configuration
    to be updated to add/remove information without modifying the code itself.
    """

    def __init__(self, bot: simplebot.SimpleBot):
        super().__init__(bot, config_name='clubInfo')

        self.__subcommands = []
        for command in self.config:
            self.__subcommands.append(command)
    
    def get_subcommands(self, ctx: discord.AutocompleteContext):
        return self.__subcommands
            
    @discord.command(name="club", description="Provides club information")
    @discord.option(name="what", description="What do you want to know about?", autocomplete=get_subcommands)
    async def club(self, 
                   ctx: discord.ApplicationContext, 
                   what: str):
        embed = self._generate_embed(what)
        await ctx.respond(embed=embed)
    
    def _generate_embed(self, info_type: str) -> discord.Embed:
        if info_type not in self.config:
            content = f"I don't have any information about '{info_type}'. Ask my owner to add some!"
            return self._embed(description=content)
        
        # If the config is just a simple string, then it should point to a file
        # on disk to read and return inline
        if isinstance(self.config[info_type], str):
            with open(self.config[info_type], 'r') as fp:
                return self._embed(description=fp.read())
        
        # The config is a dictionary of values
        config = self.config[info_type]
        embed = self._embed(
            title=config.get('title', None),
            description=config.get('description', None)
        )

        for field in config.get('fields', None):
            embed.add_field(name=field.get('name', None), value=field.get('value', None), inline=field.get('inline', True))
        
        return embed  

def setup(bot: simplebot.SimpleBot):
    bot.add_cog(ClubInfo(bot))