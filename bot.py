#!python3

import dotenv
import os
import discord

dotenv.load_dotenv('config.env')
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond('hey!')

bot.run(os.getenv('DISCORD_TOKEN'))

