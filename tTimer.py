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
            self.chanID = 796561635262464010

    def cog_unload(self):
        self.timer.cancel()

    async def updateWatchForTval(self):
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite("timer")
        await self.dataHelp.timerHelp.setTValueOfNextStoryBeat(list(timesOfBeats.keys())[len(cmpnData[len(cmpnData)-1]["Confirmed completed story beats"])])
        # t = await self.dataHelp.progHelp.getTForNoWrite()
        # timeline = [i for i in timesOfBeats.keys() if i <= t]
        # await self.dataHelp.timerHelp.setTValueOfNextStoryBeat(list(timesOfBeats.keys())[len(timeline)])

    async def stopTimersHelper(self):
        if not await self.dataHelp.timerHelp.getTimerPausedProgressStatus():
            self.timer.stop()
            await asyncio.sleep(3) #wait for timer to finish current loop
            cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
            cmpnData[len(cmpnData)-1]["Last timer tick"] = 0
            await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)
            await self.bot.get_channel(self.chanID).send("Timer stopped!")
        else:
            self.progDelayTimer.stop()
            await asyncio.sleep(3) #wait for timer to finish current loop
            await self.bot.get_channel(self.chanID).send("Progress delay timer stopped!")
    
    @commands.command(name='stopTimer', help='stops the timer that edits the t-value dynamically')
    async def stopTimer(self, ctx):
        await self.stopTimersHelper()

    async def startTtimer(self):
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
        cmpnData[len(cmpnData)-1]["Last timer tick"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
        #reset prog delay time
        cmpnData[len(cmpnData)-1]["Seconds of progress delay"] == 0.0
        await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)
        await self.updateWatchForTval()
        self.timer.start()
        await self.bot.get_channel(self.chanID).send("Timer started!")

    async def startDelaytimer(self):
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
        cmpnData[len(cmpnData)-1]["Last delay timer tick"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
        await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)
        self.progDelayTimer.start()
        await self.bot.get_channel(self.chanID).send("Progress delay timer started!")

    async def startTimersHelper(self):
        def check(msg):
            return msg.channel == self.bot.get_channel(self.chanID)

        if not await self.dataHelp.timerHelp.getTimerPausedProgressStatus(): # is progress not paused
            if not self.timer.is_running(): # is timer not running
                await self.startTtimer()
            else: # is timer running
                await self.bot.get_channel(self.chanID).send("Timer already running!")
        else: # is progress paused
            cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite("timer")
            if (not self.progDelayTimer.is_running()) and (cmpnData[len(cmpnData)-1]["Seconds of progress delay"] == 0.0): # is progDelayTimer not running
                await self.startDelaytimer()
            else: # is progDelayTimer running
                await self.stopTimersHelper()
                beforeAskDT = datetime.now(pytz.timezone('US/Eastern'))
                # check progress...
                await self.bot.get_channel(self.chanID).send("Have you reached the " + timesOfBeats[await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()] + " yet? [y/n]:")
                ans = await self.bot.wait_for('message', check=check)
                while (ans.content != 'n' and ans.content != 'y'):
                    await self.bot.get_channel(self.chanID).send("Have you reached the " + timesOfBeats[await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()] + " yet? [y/n]:")
                    ans = await self.bot.wait_for('message', check=check)

                afterAskDT = datetime.now(pytz.timezone('US/Eastern'))
                difference = relativedelta.relativedelta(afterAskDT, beforeAskDT)
                totalNumSecs = float(difference.hours*60.0*60.0 + difference.minutes*60.0 + difference.seconds)

                # ask if they have been playing while bot was waiting for its question to be answered 
                if totalNumSecs > 60.0:
                    await self.bot.get_channel(self.chanID).send("Hhhmmm... you took "+str(totalNumSecs)+" seconds to answer my question... Have you been playing (plot progressing pay) while I've been waiting? [y/n]:")
                    delayedAns = await self.bot.wait_for('message', check=check)
                    while (delayedAns.content != 'n' and delayedAns.content != 'y'):
                        await self.bot.get_channel(self.chanID).send("Hhhmmm... you took "+str(totalNumSecs)+" seconds to answer my question... Have you been playing (plot progressing pay) while I've been waiting? [y/n]:")
                        delayedAns = await self.bot.wait_for('message', check=check)

                    if delayedAns.content == 'y':
                        await self.bot.get_channel(self.chanID).send("Okay! Thank you for letting me know! I am going to adjust my clocks real quick...")
                        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
                        secsOfPlay = totalNumSecs + float(cmpnData[len(cmpnData)-1]["Seconds of progress delay"])
                        cmpnData[len(cmpnData)-1]["Seconds of progress delay"] = secsOfPlay
                        await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)

                    elif delayedAns.content == 'n':
                        await self.bot.get_channel(self.chanID).send("Okay! I just ask to make sure I don't need to adjust my clocks... moving on...")

                if ans.content == 'y':
                    #lock t
                    t = await self.dataHelp.progHelp.getTForWrite("timer")
                    #write to t
                    t = await self.dataHelp.timerHelp.getTValueOfNextStoryBeat() # set t to be the t-value for the current story beat
                    #unlock t
                    await self.dataHelp.progHelp.setT("timer", t)

                    #lock cmpnData
                    cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
                    #write to cmpnData
                    cmpnData[len(cmpnData)-1]["Last timer tick"] = datetime.now(pytz.timezone('US/Eastern')).timestamp() #reset timer tick to perpare for starting the tTimer up again
                    cmpnData[len(cmpnData)-1]["Confirmed completed story beats"].append(timesOfBeats[await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()]) #add for current story beat to the list of confirmed story beats
                    #get prog delay time
                    delay = cmpnData[len(cmpnData)-1]["Seconds of progress delay"] #store how much time was recorded during delay
                    #reset prog delay time
                    cmpnData[len(cmpnData)-1]["Seconds of progress delay"] = 0.0 #reset prog delay time in storage as the DelayTimer is stopped


                    await self.bot.get_channel(self.chanID).send("There has been a progress delay of " + str(delay) +" seconds. Would you like to update the expected campaign length to reflect this delay? [y/n]:")
                    delayAns = await self.bot.wait_for('message', check=check)
                    while (delayAns.content != 'n' and delayAns.content != 'y'):
                        await self.bot.get_channel(self.chanID).send("There has been a progress delay of " + str(delay) +" seconds. Would you like to update the expected campaign length to reflect this delay? [y/n]:")
                        delayAns = await self.bot.wait_for('message', check=check)

                    if delayAns.content == 'y':
                        #recalculate expected length to incorporate the delay
                        cmpnData[len(cmpnData)-1]["Expected length"] = cmpnData[len(cmpnData)-1]["Expected length"] + ((delay/60.0)/60.0)
                        await self.bot.get_channel(self.chanID).send("Okay, delay has been applied. Expected time from campaign start to campaign climax is now " + str(cmpnData[len(cmpnData)-1]["Expected length"]) + " hours.")
                    elif delayAns.content == 'n':
                        await self.bot.get_channel(self.chanID).send("Okay, this delay will be disregarded. Expected time from campaign start to campaign climax remains " + str(cmpnData[len(cmpnData)-1]["Expected length"]) + " hours.")

                    #update seconds played to reflect new t-value and possible time expansion
                    cmpnData[len(cmpnData)-1]["Seconds of plot play"] = (t*float(cmpnData[len(cmpnData)-1]["Expected length"]*60.0*60.0))

                    #unlock to cmpnData
                    await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)
                    #update T val to look for next
                    await self.updateWatchForTval()
                    await self.dataHelp.timerHelp.disableTimerPausedProgress()
                    await self.startTtimer()
                elif ans.content == 'n':
                    await self.startDelaytimer()
                    


    @commands.command(name='startTimer', help='starts the timer that edits the t-value dynamically')
    async def startTimer(self, ctx):
        await self.startTimersHelper()

    @commands.command(name='setTimerTargetTvalue', help='sets the t-value that the timer is looking for')
    async def setTimerTargetTvalue(self, ctx, t:float):
        await self.dataHelp.timerHelp.setTValueOfNextStoryBeat(t)
        await self.bot.get_channel(self.chanID).send("Timer target t-value set to: " + str(t))

    async def askAboutProgress(self):
        def check(msg):
            return msg.channel == self.bot.get_channel(self.chanID)

        beforeAskDT = datetime.now(pytz.timezone('US/Eastern'))
        await self.bot.get_channel(self.chanID).send("Have you reached the " + timesOfBeats[await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()] + " yet? [y/n]:")
        ans = await self.bot.wait_for('message', check=check)
        while (ans.content != 'n' and ans.content != 'y'):
            await self.bot.get_channel(self.chanID).send("Have you reached the " + timesOfBeats[await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()] + " yet? [y/n]:")
            ans = await self.bot.wait_for('message', check=check)

        afterAskDT = datetime.now(pytz.timezone('US/Eastern'))
        difference = relativedelta.relativedelta(afterAskDT, beforeAskDT)
        totalNumSecs = float(difference.hours*60.0*60.0 + difference.minutes*60.0 + difference.seconds)

        # ask if they have been playing while bot was waiting for its question to be answered
        if totalNumSecs > 60.0:
            await self.bot.get_channel(self.chanID).send("Hhhmmm... you took "+str(totalNumSecs)+" seconds to answer my question... Have you been playing (plot progressing pay) while I've been waiting? [y/n]:")
            delayedAns = await self.bot.wait_for('message', check=check)
            while (delayedAns.content != 'n' and delayedAns.content != 'y'):
                await self.bot.get_channel(self.chanID).send("Hhhmmm... you took "+str(totalNumSecs)+" seconds to answer my question... Have you been playing (plot progressing pay) while I've been waiting? [y/n]:")
                delayedAns = await self.bot.wait_for('message', check=check)

            if delayedAns.content == 'y':
                await self.bot.get_channel(self.chanID).send("Okay! Thank you for letting me know! I am going to adjust my clocks real quick...")
                cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
                secsOfPlay = totalNumSecs + float(cmpnData[len(cmpnData)-1]["Seconds of plot play"])
                secondsToClimax = cmpnData[len(cmpnData)-1]["Expected length"]*60.0*60.0
                cmpnData[len(cmpnData)-1]["Seconds of plot play"] = secsOfPlay
                cmpnData[len(cmpnData)-1]["Last timer tick"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
                await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)

                t = await self.dataHelp.progHelp.getTForWrite("timer")
                t = float(secsOfPlay)/float(secondsToClimax)
                await self.dataHelp.progHelp.setT("timer", t)

            elif delayedAns.content == 'n':
                await self.bot.get_channel(self.chanID).send("Okay! I just ask to make sure I don't need to adjust my clocks... moving on...")


        
            
        if ans.content == 'n':
            await self.bot.get_channel(self.chanID).send("Answered no. You have not reached the " + timesOfBeats[await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()] + " yet.")
            if not await self.dataHelp.timerHelp.getTimerPausedProgressStatus():
                #stop timer
                await self.stopTimersHelper()

                #lock t
                t = await self.dataHelp.progHelp.getTForWrite("timer")
                #write to t
                t = await self.dataHelp.timerHelp.getTValueOfNextStoryBeat() # set t to be the t-value for the current story beat
                #unlock t
                await self.dataHelp.progHelp.setT("timer", t)

                #lock cmpnData
                cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
                #write to cmpnData
                #update seconds played to reflect new t-value and possible time expansion
                cmpnData[len(cmpnData)-1]["Seconds of plot play"] = (t*float(cmpnData[len(cmpnData)-1]["Expected length"]*60.0*60.0))
                #unlock to cmpnData
                await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)

                # #lock cmpnData
                # cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
                # #write to cmpnData
                # cmpnData[len(cmpnData)-1]["Seconds of plot play"] = (await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()*float(cmpnData[len(cmpnData)-1]["Expected length"]*60.0*60.0))-5
                # #unlock to cmpnData
                # await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)

                # #lock t
                # t = await self.dataHelp.progHelp.getTForWrite("timer")
                # #write to t
                # t = float(cmpnData[len(cmpnData)-1]["Seconds of plot play"])/float(cmpnData[len(cmpnData)-1]["Expected length"]*60.0*60.0)
                # #unlock t
                # await self.dataHelp.progHelp.setT("timer", t)

                await self.dataHelp.timerHelp.enableTimerPausedProgress()
                #start prog delay timer
                await self.startTimersHelper()
            else:
                self.bot.get_channel(self.chanID).send("Uh oh... you are in askAboutProgress when you really should not be... what is going on??")

        elif ans.content == 'y':
            await self.bot.get_channel(self.chanID).send("Answered yes. You have reached the " + timesOfBeats[await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()] + ".")
            #lock cmpnData
            cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")
            #write to cmpnData
            cmpnData[len(cmpnData)-1]["Last timer tick"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
            cmpnData[len(cmpnData)-1]["Confirmed completed story beats"].append(timesOfBeats[await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()])


            #unlock to cmpnData
            await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)

            await self.updateWatchForTval() #update what t-val to expect for next beat

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

            await self.bot.get_channel(self.chanID).send("Seconds of play: " + str(secsOfPlay) + " | t-value: " + str(t) +" | t-value to look for: " + str(await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()))

            if t >= await self.dataHelp.timerHelp.getTValueOfNextStoryBeat():
                await self.askAboutProgress()


    @tasks.loop(seconds=2.0)
    async def progDelayTimer(self):
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite("timer")
        if cmpnData:
            cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")

            lastDT = datetime.fromtimestamp(cmpnData[len(cmpnData)-1]["Last delay timer tick"])

            nowDT = datetime.now(pytz.timezone('US/Eastern')).timestamp()
            difference = relativedelta.relativedelta(datetime.fromtimestamp(nowDT), lastDT)
            totalNumSecs = float(difference.hours*60.0*60.0 + difference.minutes*60.0 + difference.seconds)

            secsOfDelay = totalNumSecs + float(cmpnData[len(cmpnData)-1]["Seconds of progress delay"])
            print(secsOfDelay)

            cmpnData[len(cmpnData)-1]["Seconds of progress delay"] = secsOfDelay
            cmpnData[len(cmpnData)-1]["Last delay timer tick"] = nowDT

            await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)

            t = await self.dataHelp.progHelp.getTForNoWrite()
            await self.bot.get_channel(self.chanID).send("Seconds of progress delay: " + str(secsOfDelay) + " | t-value: " + str(t) +" | t-value to look for: " + str(await self.dataHelp.timerHelp.getTValueOfNextStoryBeat()))


    @tasks.loop(seconds=2.0)
    async def ansDelayTimer(self):
        cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForNoWrite("timer")
        if cmpnData:
            cmpnData = await self.dataHelp.cmpnHelp.getCmpnDataForWrite("timer")

            lastDT = datetime.fromtimestamp(cmpnData[len(cmpnData)-1]["Last delay timer tick"])

            nowDT = datetime.now(pytz.timezone('US/Eastern')).timestamp()
            difference = relativedelta.relativedelta(datetime.fromtimestamp(nowDT), lastDT)
            totalNumSecs = float(difference.hours*60.0*60.0 + difference.minutes*60.0 + difference.seconds)

            secsOfDelay = totalNumSecs + float(cmpnData[len(cmpnData)-1]["Seconds of progress delay"])
            print(secsOfDelay)

            cmpnData[len(cmpnData)-1]["Seconds of progress delay"] = secsOfDelay
            cmpnData[len(cmpnData)-1]["Last delay timer tick"] = nowDT

            await self.dataHelp.cmpnHelp.setCmpnData("timer", cmpnData)

            t = await self.dataHelp.progHelp.getTForNoWrite()