# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

"""Extension implementing a Cog providing health and status about the bot"""

import datetime
import discord
from extensions.util import simplebot

class About(simplebot.SimpleCog):
    """Implements health and status commands for the bot"""
    def __init__(self, bot: simplebot.SimpleBot):
        super().__init__(bot)

    @discord.command(name="about", description="Provides information about the bot")
    async def health_and_status(self, ctx: discord.ApplicationContext):
        """Provides health and status for the bot"""
        uptime = datetime.timedelta(seconds=round(self.bot.uptime))
        latency = round(self.bot.latency * 1000, 0)

        description="""
        A discord bot intended for use in servers for Amateur Radio Clubs. Provides a series of \
        useful tools for managing the club, looking up weather conditions for radio operation, etc.

        Find more info at [dongola7/hamclubbot](https://github.com/dongola7/hamclubbot) on GitHub.
        """

        embed = self._embed(title="About this bot", description=description)
        owner = f"<@{self.bot.owner_id}>" if self.bot.owner_id else "undefined"
        embed.add_field(name="Owner", value=owner)
        embed.add_field(name="Uptime", value=f"{uptime}")
        embed.add_field(name="Latency", value=f"{latency} ms")
        await ctx.respond(embed=embed)

def setup(bot: simplebot.SimpleBot):
    """Called when the extension is loaded"""
    bot.add_cog(About(bot))
