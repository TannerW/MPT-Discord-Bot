"""!
 @file sessionHelpers.py
 @author Owen Tanner Wilkerson (tanner.wilkerson@gmail.com)
 @brief Helpers used the operate on campaign data
 @version 0.1
 @date 2021-02-11
 
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

class SessionHelp(commands.Cog):
    def __init__(self, bot, dataHelp):
        self.bot = bot
        self.dataHelp = dataHelp

    @commands.command(name='startNewSess', help='test')
    async def startNewSess(self, ctx):
        """!
        @brief Start a new session

        @param ctx Server context
        """

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        # get name of current campaign
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite(ctx.message.author.name)
        cmpnName = cmpnData[len(cmpnData)-1]["Campaign name"] 
        sessData = await self.dataHelp.sessHelp.getSessDataForWrite(ctx.message.author.name)


        response = "Current session data " + json.dumps(sessData)
        await ctx.send(response)

        # check how many session this campaign has had
        sessionNumber = 1
        if sessData:
            for i in range(len(sessData)-1, -1, -1):
                if sessData[i]["Campaign name"] == cmpnName:
                    sessionNumber = sessData[i]["Session number"] + 1
                    if sessData[i]["Session end time"] == 0:
                        await ctx.send("Uh oh... it looks like the last session didnt end... would you like to end it now? [y/n]:")
                        ans = await self.bot.wait_for('message', check=check)
                        if ans.content == 'y':
                            sessData[i]["Session end time"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()


        temp = sessionDataDefault
        temp["Campaign name"] = cmpnName
        temp["Session number"] = sessionNumber
        temp["Session start time"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
        temp["Timestamp of last activity"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
        response = "Current session data " + json.dumps(temp)
        await ctx.send(response)

        if not sessData:
            sessData = []
            sessData.append(temp)
        else:
            sessData.append(temp)

        await self.dataHelp.sessHelp.setSessData(ctx.message.author.name, sessData)
        await self.dataHelp.sessHelp.setSessActive(ctx.message.author.name)
        await self.bot.get_cog("tTimer").startTimer(ctx)
        response = "Session started! Enjoy your adventuring!!"
        await ctx.send(response)

    @commands.command(name='endSess', help='test')
    async def endSess(self, ctx):
        """!
        @brief End session

        @param ctx Server context
        """

        sessData = await self.dataHelp.sessHelp.getSessDataForWrite(ctx.message.author.name)

        response = ""
        if sessData:
            if sessData[len(sessData)-1]["Session end time"] == 0:
                sessData[len(sessData)-1]["Session end time"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
                sessData[len(sessData)-1]["Timestamp of last activity"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
                await self.dataHelp.sessHelp.setSessData(ctx.message.author.name, sessData)
                await self.dataHelp.sessHelp.setSessInactive(ctx.message.author.name)
                await self.bot.get_cog("tTimer").stopTimer(ctx)
                response = "Session ended! I hope you enjoyed your adventuring!!"
            else:
                response = "Uh oh... looks like the session was either never started or has already ended..."
        else: 
            response = "No session data..."
                
        await ctx.send(response)

    @commands.command(name='getSessData', help='test')
    async def getSessData(self, ctx):
        """!
        @brief This command set data for the current active session

        @param ctx Server context
        """

        sessData = await self.dataHelp.sessHelp.getSessDataForNoWrite(ctx.message.author.name)
        response = "Session data set as " + json.dumps(sessData)
        print(response)
        await ctx.send(response)