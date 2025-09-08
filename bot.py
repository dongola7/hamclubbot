#!python3

import dotenv
import os
import discord

dotenv.load_dotenv('config.env')
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="conditions", description="Show current conditions from hamqsl.com")
async def conditions(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title = "Current Solar Conditions",
        description="Images from [hamqsl.com](https://www.hamqsl.com)"
    )
    embed.set_image(url="https://www.hamqsl.com/solar101pic.php")

    await ctx.respond(embed=embed)

bot.run(os.getenv('DISCORD_TOKEN'))

