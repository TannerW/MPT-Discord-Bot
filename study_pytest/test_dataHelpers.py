import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pytest
from dataHelpers import *

redisClient = redis.Redis(host='192.168.1.110', port=6381, db=1)

@pytest.mark.asyncio
async def test_cmpnHelp_match():
    lockAndKey = LockAndKey()
    cmpnHelp = CmpnDataHelp(redisClient, lockAndKey)
    testJson = campaignDataDefault
    await cmpnHelp.getCmpnDataForWrite("tester")
    await cmpnHelp.setCmpnData("tester", testJson)
    testReturn = await cmpnHelp.getCmpnDataForNoWrite("tester")
    assert testJson == testReturn,"test failed because the campnData in Redis did not match what was supposed to be written during this test."

@pytest.mark.asyncio
async def test_cmpnHelp_mismatch():
    lockAndKey = LockAndKey()
    cmpnHelp = CmpnDataHelp(redisClient, lockAndKey)
    testJson = campaignDataDefault
    testReturnOriginal = testJson.copy()
    testJson["Campaign name"] = "asdf"
    await cmpnHelp.getCmpnDataForWrite("tester")
    await cmpnHelp.setCmpnData("tester", testJson)
    testReturn = await cmpnHelp.getCmpnDataForNoWrite("tester")
    assert testReturnOriginal != testReturn,"test failed because the campnData in Redis did not mismatch what was supposed to be written during this test."

@pytest.mark.asyncio
async def test_cmpnHelp_writingLock_locked():
    lockAndKey = LockAndKey()
    cmpnHelp = CmpnDataHelp(redisClient, lockAndKey)
    testJson = campaignDataDefault
    await cmpnHelp.getCmpnDataForWrite("tester")

    try:
        await asyncio.wait_for(cmpnHelp.getCmpnDataForNoWrite("notTester"), timeout=10.0)
    except asyncio.TimeoutError:
        assert True
        return

    assert False

@pytest.mark.asyncio
async def test_cmpnHelp_writingLock_notLocked():
    lockAndKey = LockAndKey()
    cmpnHelp = CmpnDataHelp(redisClient, lockAndKey)
    testJson = campaignDataDefault
    await cmpnHelp.getCmpnDataForNoWrite("notTester")

    try:
        await asyncio.wait_for(cmpnHelp.getCmpnDataForWrite("tester"), timeout=10.0)
    except asyncio.TimeoutError:
        assert False
        return

    assert True