# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

import discord
import json
import urllib.parse
import logging
import extensions.util.simplebot as simplebot
import extensions.util.webcache as webcache

logger = logging.getLogger(__name__)

class Pota(simplebot.SimpleCog):
    """
    Implements commands for querying the Parks on the Air website.
    """

    def __init__(self, bot: simplebot.SimpleBot):
        super().__init__(bot)
        self.__cache = webcache.WebCache()

    cmd_group = discord.SlashCommandGroup(name="pota", description="Query the pota.app website for details")

    @cmd_group.command(name="callstats", description="Get POTA statistics for a specific callsign")
    @discord.option(name="callsign", description="The callsign")
    async def callstats(self, ctx: discord.ApplicationContext, callsign: str):
        """Responds with POTA statistics for the given callsign."""
        callsign = callsign.upper()
        url = f"https://api.pota.app/stats/user/{urllib.parse.quote(callsign)}"
        cache_entry = await self.__cache.getUrl(url)
        logger.debug(f"queried {url} and received {cache_entry.content}")

        result = json.loads(cache_entry.content)

        if isinstance(result, str):
            # Error message from the pota API
            await ctx.respond(f"error while querying the pota website for callsign {callsign}: {result}", ephemeral=True)
        else:
            link = f"https://pota.app/#/profile/{urllib.parse.quote(callsign)}"
            embed = self._embed(title=f"{callsign}'s POTA Stats",
                                description=f"Information provided by [pota.app](https://pota.app). See [{callsign}'s profile]({link}) for details.")

            activator = result['activator']
            attempts = result['attempts']
            activator_desc = f"{activator['activations']}/{attempts['activations']} activations in {activator['parks']}/{attempts['parks']} parks. {activator['qsos']} total QSOs."
            embed.add_field(name="Activator", value=activator_desc, inline=False)

            hunter = result['hunter']
            hunter_desc = f"{hunter['parks']} hunted parks. {hunter['qsos']} total QSOs."
            embed.add_field(name="Hunter", value=hunter_desc, inline=False)

            embed.set_footer(text=cache_entry.last_refreshed_str())

            await ctx.respond(embed=embed)

def setup(bot: simplebot.SimpleBot):
    bot.add_cog(Pota(bot))

