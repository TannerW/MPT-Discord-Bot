import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random

load_dotenv()
TOKEN = os.getenv('TOKEN')


# client = discord.Client()

bot = commands.Bot(command_prefix='>')

# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="D&D 5e | &help")); 

@bot.command(name='99', help='test')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

# @bot.event
# async def on_message(message):
#     channels = ["test"]
#     valid_users = ["Tanner#1753"]

#     if str(message.channel) in channels and str(message.author) in valid_users:
#         await message.channel.send('👋') 

bot.run(TOKEN)