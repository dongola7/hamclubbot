import discord
import webcache
import io
import cairosvg
import logging
import simplebot

logger = logging.getLogger(__name__)

class Conditions(simplebot.SimpleCog):
    """Provides a set of discord bot commands for checking radio weather conditions"""
    def __init__(self, bot: simplebot.SimpleBot):
        super().__init__(bot)
        self.__cache = webcache.WebCache()

    @discord.command(name="cond", description="Show current conditions from https://hamqsl.com")
    async def cond(self, ctx: discord.ApplicationContext):
        cache_entry = self.__cache.getUrl('https://www.hamqsl.com/solar101pic.php')
        with io.BytesIO(cache_entry.content) as content:
            file = discord.File(fp = content, filename='conditions.jpg')
            embed = self._embed(
                title = "Current Solar Conditions",
                description="Images from [hamqsl.com](https://www.hamqsl.com)"
            )
            embed.set_image(url="attachment://conditions.jpg")

            await ctx.respond(embed=embed, file=file)

    @discord.command(name="muf", description="Show current MUF map from https://prop.kc2g.com")
    async def muf(self, ctx: discord.ApplicationContext):
        URL = 'https://prop.kc2g.com/renders/current/mufd-normal-now.svg'
        cache_entry = self.__cache.getUrl(URL)

        # If there is no extra data associated with the cache, then we need to
        # convert the SVG to a PNG and cache the PNG value
        if not cache_entry.extra:
            logger.debug("converting muf map from svg to png")
            png_bytes = cairosvg.svg2png(bytestring = cache_entry.content)
            cache_entry.extra = png_bytes
        else:
            logger.debug("using cached png value of muf map")
            png_bytes = cache_entry.extra

        with io.BytesIO(png_bytes) as content:
            file = discord.File(fp = content, filename = 'mufmap.png')
            embed = self._embed(
                title = "Current MUF Map",
                description="Map from [prop.kc2g.com](https://prop.kc2g.com)"
            )
            embed.set_image(url="attachment://mufmap.png")

            await ctx.respond(embed=embed, file=file)

def setup(bot: simplebot.SimpleBot):
    logger.info("setting up extension")
    bot.add_cog(Conditions(bot))