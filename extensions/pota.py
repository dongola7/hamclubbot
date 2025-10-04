# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

"""Extension implementing a Cog to lookup pota information"""

from typing import cast
import json
import asyncio
import io
import logging
import urllib.parse

import discord

from extensions.util import simplebot, webcache

logger = logging.getLogger(__name__)

class Pota(simplebot.SimpleCog):
    """
    Implements commands for querying the Parks on the Air website.
    """

    def __init__(self, bot: simplebot.SimpleBot):
        super().__init__(bot)
        self.__cache = webcache.WebCache()

    cmd_group = discord.SlashCommandGroup(name="pota",
        description="Query the pota.app website for details")

    def _format_park_name(self, park_info):
        quoted_park = urllib.parse.quote(park_info['reference'])
        link = f"https://pota.app/#/park/{quoted_park}"
        return f"[{park_info['reference']}]({link}) - [{park_info['name']}, \
{park_info['locationName']}]({park_info['website']})"

    def _format_park_stats(self, park_stats):
        return f"{park_stats['activations']}/{park_stats['attempts']} activations, \
{park_stats['contacts']} QSOs"

    def _format_recent_activations(self, activations):
        with io.StringIO() as result:
            for a in activations:
                date = str(a['qso_date'])
                date_str = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
                print(f"* {date_str} - **{a['activeCallsign']}** - {a['totalQSOs']} QSOs",
                    file=result)
                print(f"  * {a['qsosCW']} CW, {a['qsosDATA']} Data, {a['qsosPHONE']} Phone",
                    file=result)
            return result.getvalue()

    @cmd_group.command(name="activations", description="Get recent activations for a specific park")
    @discord.option(name="park", description="The park number (e.g. US-8081)")
    async def activations(self, ctx: discord.ApplicationContext, park: str):
        """Responds with recent activations for the given park."""
        park = park.upper()
        quoted_park = urllib.parse.quote(park)

        caches = await asyncio.gather(
            self.__cache.get_url(f"https://api.pota.app/park/stats/{quoted_park}"),
            self.__cache.get_url(f"https://api.pota.app/park/{quoted_park}"),
            self.__cache.get_url(f"https://api.pota.app/park/activations/{quoted_park}?count=5")
        )
        stats_cache, info_cache, recent_cache = map(
            lambda o: cast(webcache.CacheEntry, o), caches)
        stats_result, info_result, recent_result = map(
            lambda c: json.loads(c.content), [stats_cache, info_cache, recent_cache])

        # Check for error messages
        if isinstance(stats_result, str):
            await ctx.respond(
                f"error while querying the pota website for park {park}: {stats_result}",
                ephemeral=True)
        elif isinstance(info_result, str):
            await ctx.respond(
                f"error while querying the pota website for park {park}: {info_result}",
                ephemeral=True)
        elif isinstance(recent_result, str):
            await ctx.respond(
                f"error while querying the pota website for park {park}: {recent_result}",
                ephemeral=True)
        else:
            embed = self._embed(title=f"{park} Stats",
                description="Information provided by [pota.app](https://pota.app).")
            embed.set_footer(text=recent_cache.last_refreshed_str())

            embed.add_field(name="Park Name",
                value=self._format_park_name(info_result),
                inline=False)
            embed.add_field(name="Stats",
                value=self._format_park_stats(stats_result),
                inline=False)
            embed.add_field(name="Recent Activations",
                value=self._format_recent_activations(recent_result),
                inline=False)

            await ctx.respond(embed=embed)

    @cmd_group.command(name="callstats", description="Get POTA statistics for a specific callsign")
    @discord.option(name="callsign", description="The callsign")
    async def callstats(self, ctx: discord.ApplicationContext, callsign: str):
        """Responds with POTA statistics for the given callsign."""
        callsign = callsign.upper()
        url = f"https://api.pota.app/stats/user/{urllib.parse.quote(callsign)}"
        cache_entry = await self.__cache.get_url(url)
        logger.debug("queried %s and received %s", url, cache_entry.content)

        result = json.loads(cache_entry.content)

        if isinstance(result, str):
            # Error message from the pota API
            await ctx.respond(
                f"error while querying the pota website for callsign {callsign}: {result}",
                ephemeral=True)
        else:
            link = f"https://pota.app/#/profile/{urllib.parse.quote(callsign)}"
            embed = self._embed(title=f"{callsign}'s POTA Stats",
                description=f"Information provided by [pota.app](https://pota.app).\
\n\nSee [{callsign}'s profile]({link}) for details.")

            activator = result['activator']
            attempts = result['attempts']
            activator_desc = f"{activator['activations']}/{attempts['activations']} activations in\
{activator['parks']}/{attempts['parks']} parks. {activator['qsos']} total QSOs."
            embed.add_field(name="Activator", value=activator_desc, inline=False)

            hunter = result['hunter']
            hunter_desc = f"{hunter['parks']} hunted parks. {hunter['qsos']} total QSOs."
            embed.add_field(name="Hunter", value=hunter_desc, inline=False)

            embed.set_footer(text=cache_entry.last_refreshed_str())

            await ctx.respond(embed=embed)

def setup(bot: simplebot.SimpleBot):
    """Called when the extension is loaded"""
    bot.add_cog(Pota(bot))
