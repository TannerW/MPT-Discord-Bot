import discord
from discord.ext import commands
import redis
import asyncio
import json

from datetime import datetime
from dateutil import relativedelta
import pytz

class DataHelp:
    def __init__(self, redisClient):
        self.redisClient = redisClient
        self.lock = asyncio.Lock()
        self.userWithKey = 0

    async def getCmpnDataForNoWrite(self, user):
        async with self.lock:
            print(user+": I am reading campaign data")
            return json.loads(self.redisClient.get('campaignData').decode("utf-8"))

    async def getCmpnDataForWrite(self, user):
        await self.lock.acquire()
        self.userWithKey = user
        print(self.userWithKey + " has read cmpnData and has acquired the lock for reading")
        data = self.redisClient.get('campaignData')
        if not data:
            return []
        else:
            return json.loads(data.decode("utf-8"))

    async def setCmpnData(self, user, cmpnData):
        if (self.lock.locked() and user == self.userWithKey):
            print(user+": I am writing CmpnData")
            self.redisClient.set('campaignData', json.dumps(cmpnData))
            self.userWithKey = ""
            self.lock.release()

    async def incrementNumProgRolls(self):
        async with self.lock:
            cmpnData = json.loads(self.redisClient.get('campaignData').decode("utf-8"))
            cmpnData[len(cmpnData)-1]["Total number of progress rolls"] = cmpnData[len(cmpnData)-1]["Total number of progress rolls"] + 1
            cmpnData[len(cmpnData)-1]["Timestamp of last activity"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
            self.redisClient.set('campaignData', json.dumps(cmpnData))

