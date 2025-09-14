import discord
import logging

logger = logging.getLogger(__name__)

class ClubInfo(discord.Cog):
    """Implements commands providing club information"""

    cmd_group = discord.SlashCommandGroup(name="club", description="Provides club information")

    def __init__(self, bot: discord.Bot):
        self.__bot = bot
        self.__config = bot.config['clubInfo']
        
    @cmd_group.command(name="nets", description="Information about club nets")
    async def nets(self, ctx: discord.ApplicationContext):
        embed = self._generate_embed("nets", "Club Nets")
        await ctx.respond(embed=embed)
    
    @cmd_group.command(name="meetings", description="Information about club meetings")
    async def meetings(self, ctx: discord.ApplicationContext):
        embed = self._generate_embed("meetings", "Club Meetings")
        await ctx.respond(embed=embed)
    
    @cmd_group.command(name="repeaters", description="Information about club repeaters")
    async def repeaters(self, ctx: discord.ApplicationContext):
        embed = self._generate_embed("repeaters", "Club Repeaters")
        await ctx.respond(embed=embed)
    
    def _generate_embed(self, info_type: str, title: str) -> discord.Embed:
        if info_type not in self.__config:
            content = f"I don't have any information about club {info_type}. Ask my owner to add some!"
        else:
            with open(self.__config[info_type], 'r') as fp:
                content = fp.read()

        return discord.Embed(title=title, description=content)

def setup(bot: discord.Bot):
    logger.info("setting up extension")
    bot.add_cog(ClubInfo(bot))