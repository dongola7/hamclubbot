import simplebot
import discord
import datetime

class About(simplebot.SimpleCog):
    """Implements health and status commands for the bot"""
    def __init__(self, bot: simplebot.SimpleBot):
        super().__init__(bot)

    @discord.command(name="about", description="Provides information about the bot")
    async def healthAndStatus(self, ctx: discord.ApplicationContext):
        uptime = datetime.timedelta(seconds=round(self.bot.uptime))
        latency = round(self.bot.latency * 1000, 0)

        embed = self._embed(title="About this bot")
        owner = f"<@{self.bot.owner_id}>" if self.bot.owner_id else "undefined"
        embed.add_field(name="Owner", value=owner, inline=False)
        embed.add_field(name="Uptime", value=f"{uptime}")
        embed.add_field(name="Latency", value=f"{latency} ms")
        await ctx.respond(embed=embed)

def setup(bot: simplebot.SimpleBot):
    bot.add_cog(About(bot))