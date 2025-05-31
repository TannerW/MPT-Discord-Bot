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

from dataDefaults import *
from dataHelpers import *

class CampaignHelp(commands.Cog):
        def __init__(self, bot, dataHelp):
                self.bot = bot
                self.dataHelp = dataHelp

        @commands.hybrid_command(name='startNewCmpn', help='test', description='test')
        async def startNewCmpn(self, ctx):
                """!
                @brief Start a new campaign

                @param ctx Server context
                """
                def check(msg):
                        return msg.author == ctx.author and msg.channel == ctx.channel

                cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite(ctx.author.name)
                await ctx.send(f"Type campaign name:")

                nameMsg = await self.bot.wait_for('message', check=check)
                print(nameMsg.content)

                await ctx.send(f"How many hours do you expect this campaign to take to reach the story climax?:")
                durationMsg = await self.bot.wait_for('message', check=check)

                response = "Current campaign data " + json.dumps(cmpnData)
                await ctx.send(response)

                temp = campaignDataDefault
                temp["Campaign name"] = nameMsg.content
                temp["Expected length"] = float(durationMsg.content)
                temp["Timestamp of last activity"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
                response = "Current campaign data " + json.dumps(temp)
                await ctx.send(response)

                if not cmpnData:
                        cmpnData = []
                        cmpnData.append(temp)
                else:
                        cmpnData.append(temp)

                await self.dataHelp.cmpnHelp.setCmpnData(ctx.author.name, cmpnData)
                await self.dataHelp.sessHelp.setSessInactive(ctx.author.name)
                t = await self.dataHelp.progHelp.getTForWrite(ctx.author.name)
                await self.dataHelp.progHelp.setT(ctx.author.name, 0.0)
                await self.dataHelp.timerHelp.disableTimerPausedProgress()
                response = "Set campaign name as " + nameMsg.content + "\n Would you like to start a new session now? [y/n]:"
                await ctx.send(response)
                newSessAns = await self.bot.wait_for('message', check=check)
                if newSessAns.content == 'y':
                        await self.bot.get_cog("SessionHelp").startNewSess(ctx)
                

        @commands.hybrid_command(name='getCmpnName', help='test', description='test')
        async def getCmpnName(self, ctx):
                """!
                @brief This command get the name of the current campaign

                @param ctx Server context
                """
                
                cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite(ctx.author.name)
                response = "Current campaign name is: " + json.dumps(cmpnData[len(cmpnData)-1]["Campaign name"])
                await ctx.send(response)

        # @commands.command(name='setCmpnData', help='test')
        # async def setCmpnData(self, ctx):
        #         """!
        #         @brief This command set data for the current active campaign

        #         @param ctx Server context
        #         """
        #         await self.dataHelp.cmpnHelp.getCmpnDataForWrite(ctx.message.author.name)
                
        #         cmpnName = self.redisClient.set('campaignData', campaignDataDefault)
        #         await self.dataHelp.cmpnHelp.setCmpnData(ctx.message.author.name)
        #         response = "Campaign data set as " + json.dumps(campaignDataDefault)
        #         await ctx.send(response)

        @commands.hybrid_command(name='getCmpnData', help='test', description='test')
        async def getCmpnData(self, ctx):
                """!
                @brief This command set data for the current active campaign

                @param ctx Server context
                """

                cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite(ctx.author.name)
                response = "Campaign data set as " + json.dumps(cmpnData)
                await ctx.send(response)

        @commands.hybrid_command(name='setPlayedSeconds', help='test', description='test')
        async def setPlayedSeconds(self, ctx, seconds:int):
                """!
                @brief This command sets the played seconds for the current campaign

                @param ctx Server context
                """
                
                cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite(ctx.author.name)
                cmpnData[len(cmpnData)-1]["Seconds of plot play"] = seconds
                await self.dataHelp.cmpnHelp.setCmpnData(ctx.author.name, cmpnData)
                t = await self.dataHelp.progHelp.getTForWrite(ctx.author.name)
                t = float(cmpnData[len(cmpnData)-1]["Seconds of plot play"])/float(cmpnData[len(cmpnData)-1]["Expected length"]*60.0*60.0)
                await self.dataHelp.progHelp.setT(ctx.author.name, t)

                response = "Current campaign played seconds set to: " + str(seconds)
                await ctx.send(response)