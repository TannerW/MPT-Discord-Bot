import discord
from discord.ext import commands
import redis
import asyncio
import json

from datetime import datetime
from dateutil import relativedelta
import pytz

from dataDefaults import *

class LockAndKey:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.userWithKey = ""

class CmpnDataHelp:
    def __init__(self, redisClient, lockAndKey):
        self.redisClient = redisClient
        self.lockAndKey = lockAndKey

    async def getCmpnDataForNoWrite(self, user):
        async with self.lockAndKey.lock:
            print(user+": I am reading campaign data")
            self.lockAndKey.userWithKey = ""
            return json.loads(self.redisClient.get('campaignData').decode("utf-8"))

    async def getCmpnDataForWrite(self, user):
        await self.lockAndKey.lock.acquire()
        self.lockAndKey.userWithKey = user
        print(self.lockAndKey.userWithKey + " has read cmpnData and has acquired the lock for reading")
        data = self.redisClient.get('campaignData')
        if not data:
            return []
        else:
            return json.loads(data.decode("utf-8"))

    async def setCmpnData(self, user, cmpnData):
        if (self.lockAndKey.lock.locked() and user == self.lockAndKey.userWithKey):
            print(user+": I am writing CmpnData")
            self.redisClient.set('campaignData', json.dumps(cmpnData))
            self.lockAndKey.userWithKey = ""
            self.lockAndKey.lock.release()


class SessDataHelp:
    def __init__(self, redisClient, lockAndKey):
        self.redisClient = redisClient
        self.lockAndKey = lockAndKey

    async def isSessActive(self, user):
        async with self.lockAndKey.lock:
            print(user+": I am reading isSessionActive")
            self.lockAndKey.userWithKey = ""
            return int(self.redisClient.get('isSessionActive'))

    async def setSessActive(self, user):
        async with self.lockAndKey.lock:
            self.lockAndKey.userWithKey = ""
            self.redisClient.set('isSessionActive', 1)

    async def setSessInactive(self, user):
        async with self.lockAndKey.lock:
            self.lockAndKey.userWithKey = ""
            self.redisClient.set('isSessionActive', 0)


    async def getSessDataForNoWrite(self, user):
        async with self.lockAndKey.lock:
            print(user+": I am reading session data")
            self.lockAndKey.userWithKey = ""
            return json.loads(self.redisClient.get('sessionData').decode("utf-8"))

    async def getSessDataForWrite(self, user):
        await self.lockAndKey.lock.acquire()
        self.lockAndKey.userWithKey = user
        print(self.lockAndKey.userWithKey + " has read SessData and has acquired the lock for reading")
        data = self.redisClient.get('sessionData')
        if not data:
            return []
        else:
            return json.loads(data.decode("utf-8"))

    async def setSessData(self, user, SessData):
        if (self.lockAndKey.lock.locked() and user == self.lockAndKey.userWithKey):
            print(user+": I am writing SessData")
            self.redisClient.set('sessionData', json.dumps(SessData))
            self.lockAndKey.userWithKey = ""
            self.lockAndKey.lock.release()

class ProgDataHelp:
    def __init__(self, redisClient, lockAndKey):
        self.redisClient = redisClient
        self.lockAndKey = lockAndKey

    async def getTForNoWrite(self):
        async with self.lockAndKey.lock:
            self.lockAndKey.userWithKey = ""
            return float(self.redisClient.get('t').decode("utf-8"))

    async def getTForWrite(self, user):
        await self.lockAndKey.lock.acquire()
        self.lockAndKey.userWithKey = user
        print(self.lockAndKey.userWithKey + " has read t and has acquired the lock for reading")
        return float(self.redisClient.get('t').decode("utf-8"))

    async def setT(self, user, t: float):
        if (self.lockAndKey.lock.locked() and user == self.lockAndKey.userWithKey):
            print(user+": I am writing t")
            self.redisClient.set('t', t)
            self.lockAndKey.userWithKey = ""
            self.lockAndKey.lock.release()
            print(user+": I unlocked t")

    async def incrementNumProgRolls(self):
        async with self.lockAndKey.lock:
            cmpnData = json.loads(self.redisClient.get('campaignData').decode("utf-8"))
            sessData = json.loads(self.redisClient.get('sessionData').decode("utf-8"))
            cmpnData[len(cmpnData)-1]["Total number of progress rolls"] = cmpnData[len(cmpnData)-1]["Total number of progress rolls"] + 1
            cmpnData[len(cmpnData)-1]["Timestamp of last activity"] = datetime.now(pytz.timezone('US/Eastern')).timestamp()
            sessData[len(sessData)-1]["Timestamp of last activity"] = cmpnData[len(cmpnData)-1]["Timestamp of last activity"]
            sessData[len(sessData)-1]["Number of progressiveness rolls this session"] = sessData[len(sessData)-1]["Number of progressiveness rolls this session"] + 1
            self.redisClient.set('campaignData', json.dumps(cmpnData))
            self.redisClient.set('sessionData', json.dumps(sessData))
            self.lockAndKey.userWithKey = ""

class DataHelp:
    def __init__(self, redisClient):
        self.redisClient = redisClient
        self.lockAndKey = LockAndKey()
        self.cmpnHelp = CmpnDataHelp(self.redisClient, self.lockAndKey)
        self.sessHelp = SessDataHelp(self.redisClient, self.lockAndKey)
        self.progHelp = ProgDataHelp(self.redisClient, self.lockAndKey)

