import discord
import redis
from discord.ext import tasks, commands
import json

from datetime import datetime
from dateutil import relativedelta
import pytz

from dataDefaults import *
from dataHelpers import *

class tTimer(commands.Cog):
    def __init__(self, bot, dataHelp):
            self.bot = bot
            self.dataHelp = dataHelp

    def cog_unload(self):
        self.timer.cancel()
    
    @commands.command(name='stopTimer', help='stops the timer that edits the t-value dynamically')
    async def stopTimer(self, ctx):
        self.timer.stop()
        await asyncio.sleep(3) #wait for timer to finish current loop
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
        cmpnData[len(cmpnData)-1]["Last timer tick"] = 0
        await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)

    @commands.command(name='startTimer', help='starts the timer that edits the t-value dynamically')
    async def startTimer(self, ctx):
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
        if (cmpnData[len(cmpnData)-1]["Last timer tick"] == 0):
            cmpnData[len(cmpnData)-1]["Last timer tick"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
        await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)
        self.timer.start()

    async def readyStartTimer(self):
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
        cmpnData[len(cmpnData)-1]["Last timer tick"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
        await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)
        self.timer.start()

    @tasks.loop(seconds=2.0)
    async def timer(self):
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite("timer")
        if cmpnData:
            cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")

            secondsToClimax = cmpnData[len(cmpnData)-1]["Expected length"]*60.0*60.0
            lastDT = datetime.fromtimestamp(cmpnData[len(cmpnData)-1]["Last timer tick"])

            nowDT = datetime.now(pytz.timezone('US/Eastern')).timestamp()
            difference = relativedelta.relativedelta(datetime.fromtimestamp(nowDT), lastDT)
            totalNumSecs = float(difference.hours*60.0*60.0 + difference.minutes*60.0 + difference.seconds)

            secsOfPlay = totalNumSecs + float(cmpnData[len(cmpnData)-1]["Seconds of plot play"])
            print(secsOfPlay)

            cmpnData[len(cmpnData)-1]["Seconds of plot play"] = secsOfPlay
            cmpnData[len(cmpnData)-1]["Last timer tick"] = nowDT

            await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)

            t = await self.dataHelp.progHelp.getTForWrite("timer")
            t = float(secsOfPlay)/float(secondsToClimax)
            await self.dataHelp.progHelp.setT("timer", t)