#!/bin/python3

"""!
 @file MPT.py
 @author Owen Tanner Wilkerson (tanner.wilkerson@gmail.com)
 @brief Main entry for MPT application
 @version 0.1
 @date 2021-01-30
 
 @copyright Copyright (c) 2021
 
"""

import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random
import redis
import json

from datetime import datetime
from dateutil import relativedelta
import pytz

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import math

from progressivenessHelpers import *
from dataHelpers import *
from campaignHelpers import *

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='>')

redisClient = redis.Redis(host='192.168.1.110', port=6380, db=0)

dataHelp = DataHelp(redisClient)

np.random.seed(1)

@bot.event
async def on_ready():
    """!
    @brief This function runs one the bot is ready and connected to the server
    """
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="D&D 5e | >help")); 

# @bot.event
# async def on_message(message):
#     channels = ["test"]
#     valid_users = ["Tanner#1753"]

#     if str(message.channel) in channels and str(message.author) in valid_users:
#         await message.channel.send('👋') 

bot.add_cog(ProgHelp(bot, redisClient, dataHelp))
bot.add_cog(CampaignHelp(bot, dataHelp))
bot.run(TOKEN)