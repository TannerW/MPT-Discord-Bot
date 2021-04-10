"""!
 @file adventuringDayHelpers.py
 @author Owen Tanner Wilkerson (tanner.wilkerson@gmail.com)
 @brief Helpers used the operate on adventuring day data
 @version 0.1
 @date 2021-02-13
 
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

class AdvenDayHelp(commands.Cog):
    def __init__(self, bot, dataHelp):
        self.bot = bot
        self.dataHelp = dataHelp

    @commands.command(name='startNewAdvenDay', help='test')
    async def startNewAdvenDay(self, ctx):
        """!
        @brief Start a new adventuring day

        @param ctx Server context
        """

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        # get name of current campaign
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite(ctx.message.author.name)
        cmpnName = cmpnData[len(cmpnData)-1]["Campaign name"] 
        advenDayData = await self.dataHelp.advenDayHelp.getAdvenDayDataForWrite(ctx.message.author.name)


        response = "Current session data " + json.dumps(advenDayData)
        await ctx.send(response)

        temp = advenDayDataDefault
        temp["Campaign name"] = cmpnName
        temp["AdvenDay start time"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
        await ctx.send("How many characters will be participating in this adventuring day?", tts=ttsEnabled)
        num = await self.bot.wait_for('message', check=check)

        for i in range(int(num.content)):
            await ctx.send("What is the name of character " + str(i+1) +"?", tts=ttsEnabled)
            name = await self.bot.wait_for('message', check=check)
            await ctx.send("What is " + name.content +"'s level?", tts=ttsEnabled)
            lvl = await self.bot.wait_for('message', check=check)
            temp["PCs"][name.content] = int(lvl.content)

        totalExpGoal = 0
        for i in temp["PCs"]:
            totalExpGoal = totalExpGoal + advenDayAdjExpPerChar[temp["PCs"][i]]
        temp["Experience goal"] = totalExpGoal

        response = "Current session data " + json.dumps(temp)
        await ctx.send(response)

        if not advenDayData:
            advenDayData = []
            advenDayData.append(temp)
        else:
            advenDayData.append(temp)

        await self.dataHelp.advenDayHelp.setAdvenDayData(ctx.message.author.name, advenDayData)
        response = "Adventuring day started! Enjoy your adventuring!!"
        await ctx.send(response, tts=ttsEnabled)

    # @commands.command(name='endSess', help='test')
    # async def endSess(self, ctx):
    #     """!
    #     @brief End session

    #     @param ctx Server context
    #     """

    #     sessData = await self.dataHelp.sessHelp.getSessDataForWrite(ctx.message.author.name)

    #     response = ""
    #     if sessData:
    #         if sessData[len(sessData)-1]["Session end time"] == 0:
    #             sessData[len(sessData)-1]["Session end time"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
    #             sessData[len(sessData)-1]["Timestamp of last activity"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
    #             await self.dataHelp.sessHelp.setSessData(ctx.message.author.name, sessData)
    #             await self.dataHelp.sessHelp.setSessInactive(ctx.message.author.name)
    #             await self.bot.get_cog("tTimer").stopTimer(ctx)
    #             response = "Session ended! I hope you enjoyed your adventuring!!"
    #         else:
    #             response = "Uh oh... looks like the session was either never started or has already ended..."
    #     else: 
    #         response = "No session data..."
    #         await self.dataHelp.sessHelp.setSessData(ctx.message.author.name, sessData)
                
    #     await ctx.send(response, tts=ttsEnabled)

    # @commands.command(name='getSessData', help='test')
    # async def getSessData(self, ctx):
    #     """!
    #     @brief This command set data for the current active session

    #     @param ctx Server context
    #     """

    #     sessData = await self.dataHelp.sessHelp.getSessDataForNoWrite(ctx.message.author.name)
    #     response = "Session data set as " + json.dumps(sessData)
    #     print(response)
    #     await ctx.send(response)