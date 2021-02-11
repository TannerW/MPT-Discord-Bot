"""!
 @file campaignHelpers.py
 @author Owen Tanner Wilkerson (tanner.wilkerson@gmail.com)
 @brief Helpers used the operate on campaign data
 @version 0.1
 @date 2021-01-30
 
 @copyright Copyright (c) 2021
 
"""

import discord
import redis
from discord.ext import commands
import json

from datetime import datetime
from dateutil import relativedelta
import pytz

from dataHelpers import *

campaignDataDefault = {
    "Campaign name" : "Playtest Campaign 1",
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

class CampaignHelp(commands.Cog):
        def __init__(self, bot, dataHelp):
                self.bot = bot
                self.dataHelp = dataHelp

        @commands.command(name='startNewCmpn', help='test')
        async def startNewCmpn(self, ctx):
                """!
                @brief Start a new campaign

                @param ctx Server context
                """
                cmpnData = await self.dataHelp.getCmpnDataForWrite(ctx.message.author.name)
                await ctx.send(f"Type campaign name:")

                def check(msg):
                        return msg.author == ctx.author and msg.channel == ctx.channel

                nameMsg = await self.bot.wait_for('message', check=check)
                print(nameMsg.content)

                await ctx.send(f"How many hours do you expect this campaign to take:")
                durationMsg = await self.bot.wait_for('message', check=check)

                response = "Current campaign data " + json.dumps(cmpnData)
                await ctx.send(response)

                temp = campaignDataDefault
                temp["Campaign name"] = nameMsg.content
                temp["Expected length"] = int(durationMsg.content)
                temp["Timestamp of last activity"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
                response = "Current campaign data " + json.dumps(temp)
                await ctx.send(response)

                if not cmpnData:
                        cmpnData = []
                        cmpnData.append(temp)
                else:
                        cmpnData.append(temp)

                await self.dataHelp.setCmpnData(ctx.message.author.name, cmpnData)
                response = "Set campaign name as " + nameMsg.content
                await ctx.send(response)

        @commands.command(name='getCmpnName', help='test')
        async def getCmpnName(self, ctx):
                """!
                @brief This command get the name of the current campaign

                @param ctx Server context
                """
                
                cmpnData = await self.dataHelp.getCmpnDataForNoWrite(ctx.message.author.name)
                response = "Current campaign name is: " + json.dumps(cmpnData[len(cmpnData)-1]["Campaign name"])
                await ctx.send(response)

        # @commands.command(name='setCmpnData', help='test')
        # async def setCmpnData(self, ctx):
        #         """!
        #         @brief This command set data for the current active campaign

        #         @param ctx Server context
        #         """
        #         await self.dataHelp.getCmpnDataForWrite(ctx.message.author.name)
                
        #         cmpnName = self.redisClient.set('campaignData', campaignDataDefault)
        #         await self.dataHelp.setCmpnData(ctx.message.author.name)
        #         response = "Campaign data set as " + json.dumps(campaignDataDefault)
        #         await ctx.send(response)

        @commands.command(name='getCmpnData', help='test')
        async def getCmpnData(self, ctx):
                """!
                @brief This command set data for the current active campaign

                @param ctx Server context
                """

                cmpnData = await self.dataHelp.getCmpnDataForNoWrite(ctx.message.author.name)
                response = "Campaign data set as " + json.dumps(cmpnData)
                await ctx.send(response)