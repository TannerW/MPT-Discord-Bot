"""!
 @file sessionHelpers.py
 @author Owen Tanner Wilkerson (tanner.wilkerson@gmail.com)
 @brief Helpers used the operate on session data
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

    @commands.hybrid_command(name='startnewsess', help='Starts a new gaming session for the current campaign.', description='Begins a new session, linking it to the current campaign and starting the session timer.')
    async def startnewsess(self, ctx):
        """!
        @brief Start a new session

        @param ctx Server context
        """

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        # get name of current campaign
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite(ctx.author.name)
        cmpnName = cmpnData[len(cmpnData)-1]["Campaign name"] 
        sessData = await self.dataHelp.sessHelp.getSessDataForWrite(ctx.author.name)


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

        await self.dataHelp.sessHelp.setSessData(ctx.author.name, sessData)
        await self.dataHelp.sessHelp.setSessActive(ctx.author.name)
        await self.bot.get_cog("tTimer").starttimer(ctx)
        response = "Session started! Enjoy your adventuring!!"
        await ctx.send(response)

    @commands.hybrid_command(name='endsess', help='Ends the current gaming session.', description='Finalizes the current session, recording the end time and stopping the session timer.')
    async def endsess(self, ctx):
        """!
        @brief End session

        @param ctx Server context
        """

        sessData = await self.dataHelp.sessHelp.getSessDataForWrite(ctx.author.name)

        response = ""
        if sessData:
            if sessData[len(sessData)-1]["Session end time"] == 0:
                sessData[len(sessData)-1]["Session end time"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
                sessData[len(sessData)-1]["Timestamp of last activity"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
                await self.dataHelp.sessHelp.setSessData(ctx.author.name, sessData)
                await self.dataHelp.sessHelp.setSessInactive(ctx.author.name)
                await self.bot.get_cog("tTimer").stoptimer(ctx)
                response = "Session ended! I hope you enjoyed your adventuring!!"
            else:
                response = "Uh oh... looks like the session was either never started or has already ended..."
        else: 
            response = "No session data..."
            await self.dataHelp.sessHelp.setSessData(ctx.author.name, sessData)
                
        await ctx.send(response)

    @commands.hybrid_command(name='getsessdata', help='Retrieves all data for the current session.', description='Gets and displays all stored data for the currently active gaming session.')
    async def getsessdata(self, ctx):
        """!
        @brief This command set data for the current active session

        @param ctx Server context
        """

        sessData = await self.dataHelp.sessHelp.getSessDataForNoWrite(ctx.author.name)
        response = "Session data set as " + json.dumps(sessData)
        print(response)
        await ctx.send(response)