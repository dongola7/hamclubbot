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
        else:
            with open(self.config[info_type], 'r') as fp:
                content = fp.read()

        return self._embed(description=content)

def setup(bot: discord.Bot):
    logger.info("setting up extension")
    bot.add_cog(ClubInfo(bot))