#!python3

import dotenv
import os
import io
import discord
import webcache

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

bot.run(os.getenv('DISCORD_TOKEN'))