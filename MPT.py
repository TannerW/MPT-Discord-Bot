#!/bin/python3

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

load_dotenv()
TOKEN = os.getenv('TOKEN')


campaignDataDefault = {
    "Campaign Name" : "Playtest Campaign 1",
    "Timestamp of last activity" : datetime.now(pytz.timezone('US/Eastern')).timestamp(),
    "Expected length" : 20,
    "Number of completed sessions" : 0,
    "Total number of progress rolls" : 0,
    "Average number of progressiveness rolls per minute" : 0
}

sessionDataDefault = {
    "Campaign name" : "Playtest Campaign 1",
    "Session number" : 1,
    "Timestamp of last activity" : datetime.now(pytz.timezone('US/Eastern')).timestamp(),
    "Session start time" : datetime.now(pytz.timezone('US/Eastern')).timestamp(),
    "Session end time" : 0,
    "Number of progressiveness rolls this session" : 0,
    "Current number of progressiveness rolls per minute" : 0
}

advenDayDataDefault = {
    "Campaign name" : "Playtest Campaign 1",
    "AdvenDay start time" : datetime.now(pytz.timezone('US/Eastern')).timestamp(),
    "Combat density" : 5,
    "Combat lethality" : 5,
    "Experience goal" : 100000000,
    "Current experience" : 0
}


# client = discord.Client()

bot = commands.Bot(command_prefix='>')

redisClient = redis.Redis(host='192.168.1.110', port=6380, db=0)

# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')

"""
@brief this is a test
"""
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="D&D 5e | >help")); 

@bot.command(name='setCmpnName', help='test')
async def setCmpnName(ctx):
    await ctx.send(f"Type campaign name:")

    def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

    msg = await bot.wait_for('message', check=check)
    print(msg.content)
    redisClient.set('campaignName', msg.content)
    response = "Set campaign name as " + msg.content
    await ctx.send(response)

@bot.command(name='getCmpnName', help='test')
async def getCmpnName(ctx):
    
    cmpnName = redisClient.get('campaignName').decode("utf-8")
    response = "Current campaign name is: " + cmpnName
    await ctx.send(response)

@bot.command(name='getCmpnData', help='test')
async def getCmpnData(ctx):
    
    cmpnName = redisClient.set('campaignData', json.dumps(campaignDataDefault))
    response = "Campaign data set as " + json.dumps(campaignDataDefault)
    await ctx.send(response)

@bot.command(name='setT', help='Set the time and print out the growth lotus, the distribution, and alpha/beta values')
async def setT(ctx, t):
    t = float(t)
    redisClient.set('t', t)
    PlotGrowthCurve(t)
    GraphProgressivenessRoll(t)
    await ctx.send(file=discord.File('plotImage.png'))
    await ctx.send(file=discord.File('lotus.png'))
    await ctx.send(file=discord.File('lotusOverlay.png'))
    await ctx.send(file=discord.File('distribution.png'))
    alpha, beta = getAlphaAndBeta(t)
    response = "t = " + str(t) + " | alpha = " + str(alpha) + " | beta = " + str(beta)
    await ctx.send(response)

@bot.command(name='getT', help='Print current T value and growth lotus')
async def getT(ctx):
    t = float(redisClient.get('t').decode("utf-8"))
    PlotGrowthCurve(t)
    await ctx.send(file=discord.File('lotusOverlay.png'))
    alpha, beta = getAlphaAndBeta(t)
    response = "t = " + str(t) + " | alpha = " + str(alpha) + " | beta = " + str(beta)
    await ctx.send(response)

@bot.command(name='printDistribution', help='Print plot of current distribution')
async def printDistribution(ctx):
    
    t = float(redisClient.get('t').decode("utf-8"))
    GraphProgressivenessRoll(t)
    await ctx.send(file=discord.File('distribution.png'))
    response = "t = " + str(t)
    await ctx.send(response)

@bot.command(name='rollProg', help='Roll Progressiveness')
async def rollProg(ctx):
    
    t = float(redisClient.get('t').decode("utf-8"))
    result = RollProgressiveness(t)
    response = str(result)
    await ctx.send(response)

@bot.command(name='rollAlign', help='Roll Alignment')
async def rollAlign(ctx):
    
    d20 = np.random.randint(1,20)
    response = str(d20) + " - "
    if (d20 >= 1 and d20 <=5):
        response = response + "Bad"
    elif (d20 >= 6 and d20 <=8):
        response = response + "Neutral leaning bad"
    elif (d20 >= 9 and d20 <=12):
        response = response + "True Neutral"
    elif (d20 >= 13 and d20 <=15):
        response = response + "Neutral leaning good"
    elif (d20 >= 16 and d20 <=20):
        response = response + "Good"
    await ctx.send(response)

# @bot.event
# async def on_message(message):
#     channels = ["test"]
#     valid_users = ["Tanner#1753"]

#     if str(message.channel) in channels and str(message.author) in valid_users:
#         await message.channel.send('👋') 

bot.run(TOKEN)