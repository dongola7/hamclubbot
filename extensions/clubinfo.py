import discord
import logging
import extensions.basecog

logger = logging.getLogger(__name__)

class ClubInfo(extensions.basecog.Cog):
    """Implements commands providing club information"""

    cmd_group = discord.SlashCommandGroup(name="club", description="Provides club information")

    def __init__(self, bot: discord.Bot):
        super().__init__(bot, config_name='clubInfo')
        
    @cmd_group.command(name="nets", description="Information about club nets")
    async def nets(self, ctx: discord.ApplicationContext):
        embed = self._generate_embed("nets")
        await ctx.respond(embed=embed)
    
    @cmd_group.command(name="meetings", description="Information about club meetings")
    async def meetings(self, ctx: discord.ApplicationContext):
        embed = self._generate_embed("meetings")
        await ctx.respond(embed=embed)
    
    @cmd_group.command(name="repeaters", description="Information about club repeaters")
    async def repeaters(self, ctx: discord.ApplicationContext):
        embed = self._generate_embed("repeaters")
        await ctx.respond(embed=embed)
    
    def _generate_embed(self, info_type: str) -> discord.Embed:
        if info_type not in self.config:
            content = f"I don't have any information about club {info_type}. Ask my owner to add some!"
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

def setup(bot: discord.Bot):
    logger.info("setting up extension")
    bot.add_cog(ClubInfo(bot))