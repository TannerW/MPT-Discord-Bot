import unittest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import asyncio # For mocking sleep

import discord
from discord.ext import commands, tasks # Import tasks explicitly
# We might need to specifically mock discord.ext.tasks.Loop if just mocking methods isn't enough

import datetime as datetime_module
import pytz

# Adjust path to import cogs and dataHelpers
import sys
sys.path.append('../..')
import tTimer as tTimer_module # Rename to avoid conflict with class tTimer
from dataDefaults import timesOfBeats # Used in some command logic/messages

# Global for bot.wait_for mock responses
mock_user_messages_ttimer = []

class TestTTimer(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.bot = AsyncMock(spec=commands.Bot)
        # Mock loop attribute for bot if create_task is used by tasks extension
        self.bot.loop = AsyncMock(spec=asyncio.AbstractEventLoop)

        self.data_mock = Mock() # Top-level mock for dataHelp
        self.data_mock.timerHelp = AsyncMock()
        self.data_mock.cmpnHelp = AsyncMock()
        self.data_mock.progHelp = AsyncMock() # Used by updateWatchForTval & timer loop

        # Mock the channel send for background tasks/helpers
        self.mock_timer_channel = AsyncMock(spec=discord.TextChannel)
        self.bot.get_channel.return_value = self.mock_timer_channel

        # Instantiate the cog
        # We need to prevent @tasks.loop from starting real loops during instantiation or tests
        # Patch the loop methods directly on the class before instantiation for broad effect,
        # or on the instance afterwards if more granular control is needed per test.
        # For now, assume we'll control them by not calling .start() or by patching their .start/.stop.

        # Let's try patching the task methods on the class itself before making an instance
        # This prevents them from being actual discord.ext.tasks.Loop objects if not careful
        # A better way might be to allow them to be Loop objects, then mock their start/stop/is_running.

        # For now, let's create the cog instance and then patch the loop methods on the instance.
        self.cog = tTimer_module.tTimer(self.bot, self.data_mock)

        # Mock the @tasks.loop decorated methods on the instance
        # This prevents them from actually running their loop bodies during tests.
        # We make them AsyncMocks so their .start(), .stop(), .is_running() can be called/mocked.
        self.cog.timer = AsyncMock(spec=tasks.Loop) # Use tasks.Loop
        self.cog.timer.is_running = Mock(return_value=False) # Default to not running

        self.cog.progDelayTimer = AsyncMock(spec=tasks.Loop) # Use tasks.Loop
        self.cog.progDelayTimer.is_running = Mock(return_value=False)

        self.cog.ansDelayTimer = AsyncMock(spec=tasks.Loop) # Use tasks.Loop
        self.cog.ansDelayTimer.is_running = Mock(return_value=False)


        self.ctx = AsyncMock(spec=commands.Context)
        self.ctx.message = Mock()
        self.ctx.message.author = Mock(spec=discord.Member)
        self.ctx.message.author.name = "TestUser"
        self.ctx.author = self.ctx.message.author # For check functions
        self.ctx.channel = self.mock_timer_channel # Commands might send to ctx.channel or specific timer channel
        self.ctx.send = AsyncMock()


        global mock_user_messages_ttimer
        mock_user_messages_ttimer = []

        async def mock_wait_for_ttimer(event, check):
            self.assertEqual(event, 'message')
            # The check in tTimer is: msg.channel == self.bot.get_channel(self.chanID)
            # So, the mock message needs to come from self.mock_timer_channel
            if mock_user_messages_ttimer:
                msg = mock_user_messages_ttimer.pop(0)
                if check(msg): # check will use msg.channel
                    return msg
            raise asyncio.TimeoutError("No message for ttimer test")
        self.bot.wait_for = mock_wait_for_ttimer

        # Set ttsEnabled for the module (if used by helpers)
        tTimer_module.ttsEnabled = False


    async def test_setTimerTargetTvalue(self):
        target_t = 0.25
        await self.cog.setTimerTargetTvalue.callback(self.cog, self.ctx, target_t)

        self.data_mock.timerHelp.setTValueOfNextStoryBeat.assert_called_once_with(target_t)
        # Check message sent to the specific timer channel, not ctx.send
        self.mock_timer_channel.send.assert_called_once_with("Timer target t-value set to: " + str(target_t))


    @patch('tTimer.asyncio.sleep', return_value=None) # Mock sleep to prevent test delays
    @patch('tTimer.datetime', new_callable=MagicMock) # Mock datetime
    async def test_stopTimer_timer_was_running(self, mock_datetime_class, mock_sleep):
        # Setup: Timer is running, progress is not paused
        self.data_mock.timerHelp.getTimerPausedProgressStatus.return_value = False
        self.cog.timer.is_running.return_value = True # Make sure it thinks it's running to stop it

        mock_campaign_data = [{"Last timer tick": 12345, "other_data": "data"}]
        self.data_mock.cmpnHelp.getCmpnDataForWrite.return_value = mock_campaign_data

        await self.cog.stopTimer.callback(self.cog, self.ctx) # Call the command

        self.cog.timer.stop.assert_called_once()
        mock_sleep.assert_called_once_with(3)
        self.data_mock.cmpnHelp.getCmpnDataForWrite.assert_called_once_with("timer")

        # Check that "Last timer tick" was reset
        expected_campaign_data_after_stop = [{"Last timer tick": 0, "other_data": "data"}]
        self.data_mock.cmpnHelp.setCmpnData.assert_called_once_with("timer", expected_campaign_data_after_stop)
        self.mock_timer_channel.send.assert_called_once_with("Timer stopped!")


    @patch('tTimer.asyncio.sleep', return_value=None)
    @patch('tTimer.datetime', new_callable=MagicMock)
    async def test_stopTimer_progDelayTimer_was_running(self, mock_datetime_class, mock_sleep):
        # Setup: Progress is paused, so progDelayTimer should be the one considered
        self.data_mock.timerHelp.getTimerPausedProgressStatus.return_value = True
        self.cog.progDelayTimer.is_running.return_value = True # Make it seem like progDelayTimer is running

        await self.cog.stopTimer.callback(self.cog, self.ctx)

        self.cog.progDelayTimer.stop.assert_called_once()
        mock_sleep.assert_called_once_with(3)
        self.mock_timer_channel.send.assert_called_once_with("Progress delay timer stopped!")
        # Ensure regular timer wasn't stopped and no cmpnData writing for it
        self.cog.timer.stop.assert_not_called()
        self.data_mock.cmpnHelp.getCmpnDataForWrite.assert_not_called()


    @patch('tTimer.datetime', new_callable=MagicMock)
    async def test_startTimer_normal_timer_starts(self, mock_datetime_class):
        # Setup: Progress not paused, timer not running
        self.data_mock.timerHelp.getTimerPausedProgressStatus.return_value = False
        self.cog.timer.is_running.return_value = False

        mock_now_ts = datetime_module.datetime(2023, 1,1,12,0,0, tzinfo=pytz.timezone('US/Eastern')).timestamp()
        mock_datetime_class.now.return_value.timestamp.return_value = mock_now_ts

        # Mock for updateWatchForTval
        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.return_value = [{"Confirmed completed story beats": []}] # For updateWatchForTval
        # Assuming timesOfBeats is imported and available
        first_story_beat_t = list(tTimer_module.timesOfBeats.keys())[0]

        # Mock campaign data for setting "Last timer tick"
        mock_campaign_data = [{"Last timer tick": 0, "Seconds of progress delay": 10.0}] # Has some delay to be reset
        self.data_mock.cmpnHelp.getCmpnDataForWrite.return_value = mock_campaign_data

        await self.cog.startTimer.callback(self.cog, self.ctx) # Call the command

        # Check data manipulations for startTtimer
        self.data_mock.cmpnHelp.getCmpnDataForWrite.assert_called_once_with("timer")
        expected_campaign_data_after_start = [{"Last timer tick": mock_now_ts, "Seconds of progress delay": 0.0}]
        self.data_mock.cmpnHelp.setCmpnData.assert_called_once_with("timer", expected_campaign_data_after_start)

        # Check updateWatchForTval calls
        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.assert_called_once_with("timer")
        self.data_mock.timerHelp.setTValueOfNextStoryBeat.assert_called_once_with(first_story_beat_t)

        self.cog.timer.start.assert_called_once()
        self.mock_timer_channel.send.assert_any_call("Timer started!") # Using any_call due to other potential messages by helpers


    @patch('tTimer.datetime', new_callable=MagicMock)
    async def test_startTimer_timer_already_running(self, mock_datetime_class):
        self.data_mock.timerHelp.getTimerPausedProgressStatus.return_value = False
        self.cog.timer.is_running.return_value = True # Timer is already running

        await self.cog.startTimer.callback(self.cog, self.ctx)

        self.cog.timer.start.assert_not_called() # Should not attempt to start again
        self.mock_timer_channel.send.assert_called_once_with("Timer already running!")

    # More tests will be needed for the complex paths in startTimersHelper (progress paused scenarios)
    # and askAboutProgress. Those will require careful mocking of bot.wait_for sequences.

if __name__ == '__main__':
    unittest.main()

# Note: To fully test tTimer, especially the loops and askAboutProgress,
# one might need to manually call the loop iteration methods (e.g., await self.cog.timer._loop_body())
# or use a more advanced testing approach for discord.ext.tasks, possibly by providing a mock
# event loop to the task and controlling its execution.
# The current approach of mocking the Loop objects themselves via AsyncMock(spec=commands.tasks.Loop)
# is primarily to test that commands try to start/stop them correctly, not to test the loop bodies.
# Testing the loop bodies would be more akin to integration testing or require deeper framework mocking.
