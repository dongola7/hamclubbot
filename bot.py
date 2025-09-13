#!python3

import dotenv
import os
import io
import discord
import webcache
import cairosvg

dotenv.load_dotenv('config.env')
bot = discord.Bot()
cache = webcache.WebCache()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="conditions", description="Show current conditions from https://hamqsl.com")
async def conditions(ctx: discord.ApplicationContext):
    cache_entry = cache.getUrl('https://www.hamqsl.com/solar101pic.php')
    with io.BytesIO(cache_entry['content']) as content:
        file = discord.File(fp = content, filename='conditions.jpg')
        embed = discord.Embed(
            title = "Current Solar Conditions",
            description="Images from [hamqsl.com](https://www.hamqsl.com)"
        )
        embed.set_image(url="attachment://conditions.jpg")

        await ctx.respond(embed=embed, file=file)

@bot.slash_command(name="muf", description="Show current MUF map from https://prop.kc2g.com")
async def muf(ctx: discord.ApplicationContext):
    URL = 'https://prop.kc2g.com/renders/current/mufd-normal-now.svg'
    cache_entry = cache.getUrl(URL)

    # If there is no extra data associated with the cache, then we need to
    # convert the SVG to a PNG and cache the PNG value
    if 'extra' not in cache_entry:
        png_bytes = cairosvg.svg2png(bytestring = cache_entry['content'])
        cache.cacheRelatedData(URL, png_bytes)
    else:
        png_bytes = cache_entry['extra']

    with io.BytesIO(png_bytes) as content:
        file = discord.File(fp = content, filename = 'mufmap.png')
        embed = discord.Embed(
            title = "Current MUF Map",
            description="Map from [prop.kc2g.com](https://prop.kc2g.com)"
        )
        embed.set_image(url="attachment://mufmap.png")

        await ctx.respond(embed=embed, file=file)

bot.run(os.getenv('DISCORD_TOKEN'))