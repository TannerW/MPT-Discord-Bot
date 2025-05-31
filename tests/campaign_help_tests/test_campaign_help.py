import unittest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import discord
from discord.ext import commands
import json
from datetime import datetime # This is the class datetime
import datetime as datetime_module # This is the module datetime
import pytz

# Adjust path to import cogs and dataHelpers
import sys
sys.path.append('../..')
import campaignHelpers
import dataHelpers # Will be mocked
from dataDefaults import campaignDataDefault # For startNewCmpn test

# A global to help with bot.wait_for
# Will store a list of mock messages to be returned in order
mock_user_messages = []

class TestCampaignHelp(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.bot = AsyncMock(spec=commands.Bot)
        self.data_mock = Mock() # Top-level mock for dataHelp
        self.data_mock.cmpnHelp = AsyncMock()
        self.data_mock.sessHelp = AsyncMock()
        self.data_mock.progHelp = AsyncMock()
        self.data_mock.timerHelp = AsyncMock()

        self.cog = campaignHelpers.CampaignHelp(self.bot, self.data_mock)

        self.ctx = AsyncMock(spec=commands.Context)
        self.ctx.message = Mock()
        self.ctx.message.author = Mock(spec=discord.Member) # Use Member for author
        self.ctx.message.author.name = "TestUser"
        self.ctx.author = self.ctx.message.author # check function in startNewCmpn uses ctx.author
        self.ctx.channel = Mock(spec=discord.TextChannel) # Used by check function
        self.ctx.send = AsyncMock()

        # Reset mock_user_messages for each test
        global mock_user_messages
        mock_user_messages = []

        # Mock for bot.wait_for
        async def mock_wait_for(event, check):
            self.assertEqual(event, 'message')
            # Simulate the check function
            # In the actual code, check(msg) is msg.author == ctx.author and msg.channel == ctx.channel
            # Our mock message should satisfy this.
            if mock_user_messages:
                msg = mock_user_messages.pop(0)
                if check(msg):
                    return msg
            raise asyncio.TimeoutError("No message") # Should not happen if test is set up correctly
        self.bot.wait_for = mock_wait_for

        # Mock for bot.get_cog and the subsequent call to startNewSess
        self.mock_session_cog = AsyncMock()
        self.mock_session_cog.startNewSess = AsyncMock()
        self.bot.get_cog.return_value = self.mock_session_cog


    @patch('campaignHelpers.datetime', new_callable=MagicMock) # Patch: Replace campaignHelpers.datetime (the class) with a MagicMock
    async def test_startNewCmpn_yes_to_new_session(self, mock_datetime_class):
        campaignHelpers.ttsEnabled = False # Set ttsEnabled directly in the module
        # Setup mock return values for dataHelp methods
        self.data_mock.cmpnHelp.getCmpnDataForWrite.return_value = [] # No existing campaign data
        self.data_mock.progHelp.getTForWrite.return_value = 0.0 # Initial T value

        # Configure the .now() method on our mock datetime class
        mock_now_dt_object = datetime_module.datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
        mock_datetime_class.now.return_value = mock_now_dt_object

        # Prepare mock user responses for bot.wait_for
        global mock_user_messages
        mock_campaign_name_msg = Mock(spec=discord.Message)
        mock_campaign_name_msg.content = "Test Campaign"
        mock_campaign_name_msg.author = self.ctx.author
        mock_campaign_name_msg.channel = self.ctx.channel

        mock_duration_msg = Mock(spec=discord.Message)
        mock_duration_msg.content = "100" # hours
        mock_duration_msg.author = self.ctx.author
        mock_duration_msg.channel = self.ctx.channel

        mock_new_session_ans_msg = Mock(spec=discord.Message)
        mock_new_session_ans_msg.content = "y"
        mock_new_session_ans_msg.author = self.ctx.author
        mock_new_session_ans_msg.channel = self.ctx.channel

        mock_user_messages = [mock_campaign_name_msg, mock_duration_msg, mock_new_session_ans_msg]

        await self.cog.startNewCmpn.callback(self.cog, self.ctx)

        self.data_mock.cmpnHelp.getCmpnDataForWrite.assert_called_once_with("TestUser")

        expected_campaign_data_item = campaignDataDefault.copy()
        expected_campaign_data_item["Campaign name"] = "Test Campaign"
        expected_campaign_data_item["Expected length"] = 100.0
        expected_campaign_data_item["Timestamp of last activity"] = mock_now_dt_object.timestamp()

        self.data_mock.cmpnHelp.setCmpnData.assert_called_once_with("TestUser", [expected_campaign_data_item])
        self.data_mock.sessHelp.setSessInactive.assert_called_once_with("TestUser")
        self.data_mock.progHelp.getTForWrite.assert_called_once_with("TestUser")
        self.data_mock.progHelp.setT.assert_called_once_with("TestUser", 0.0)
        self.data_mock.timerHelp.disableTimerPausedProgress.assert_called_once()

        self.assertEqual(self.ctx.send.call_count, 5) # 2 initial prompts, 2 data echos, 1 final prompt
        self.ctx.send.assert_any_call("Type campaign name:", tts=False) # Assuming ttsEnabled is False or not set
        self.ctx.send.assert_any_call("How many hours do you expect this campaign to take to reach the story climax?:", tts=False)

        # Check the final prompt for starting a new session
        self.ctx.send.assert_any_call("Set campaign name as Test Campaign\n Would you like to start a new session now? [y/n]:", tts=False)

        self.bot.get_cog.assert_called_once_with("SessionHelp")
        self.mock_session_cog.startNewSess.assert_called_once_with(self.ctx)


    @patch('campaignHelpers.datetime', new_callable=MagicMock) # Patch
    async def test_startNewCmpn_no_to_new_session(self, mock_datetime_class): # Order matters
        campaignHelpers.ttsEnabled = False # Set ttsEnabled directly in the module
        self.data_mock.cmpnHelp.getCmpnDataForWrite.return_value = None # Simulating no pre-existing data list
        self.data_mock.progHelp.getTForWrite.return_value = 0.1 # Some existing T

        mock_now_dt_object = datetime_module.datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
        mock_datetime_class.now.return_value = mock_now_dt_object

        global mock_user_messages
        mock_campaign_name_msg = Mock(spec=discord.Message, content="Another Campaign", author=self.ctx.author, channel=self.ctx.channel)
        mock_duration_msg = Mock(spec=discord.Message, content="50", author=self.ctx.author, channel=self.ctx.channel)
        mock_new_session_ans_msg = Mock(spec=discord.Message, content="n", author=self.ctx.author, channel=self.ctx.channel)
        mock_user_messages = [mock_campaign_name_msg, mock_duration_msg, mock_new_session_ans_msg]

        await self.cog.startNewCmpn.callback(self.cog, self.ctx)

        expected_campaign_data_item = campaignDataDefault.copy()
        expected_campaign_data_item["Campaign name"] = "Another Campaign"
        expected_campaign_data_item["Expected length"] = 50.0
        expected_campaign_data_item["Timestamp of last activity"] = mock_now_dt_object.timestamp()

        # cmpnData was None, so a new list is created
        self.data_mock.cmpnHelp.setCmpnData.assert_called_once_with("TestUser", [expected_campaign_data_item])
        self.data_mock.progHelp.setT.assert_called_once_with("TestUser", 0.0)

        self.mock_session_cog.startNewSess.assert_not_called()


    async def test_getCmpnName(self):
        mock_campaign_list = [
            {"Campaign name": "Old Campaign"},
            {"Campaign name": "Current Campaign"}
        ]
        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.return_value = mock_campaign_list

        await self.cog.getCmpnName.callback(self.cog, self.ctx)

        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.assert_called_once_with("TestUser")
        expected_response = 'Current campaign name is: "Current Campaign"' # Note json.dumps adds quotes
        self.ctx.send.assert_called_once_with(expected_response)


    async def test_getCmpnData(self):
        mock_campaign_list = [
            {"Campaign name": "Campaign Alpha", "Expected length": 50},
            {"Campaign name": "Campaign Beta", "Expected length": 75}
        ]
        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.return_value = mock_campaign_list

        await self.cog.getCmpnData.callback(self.cog, self.ctx)

        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.assert_called_once_with("TestUser")
        expected_response = "Campaign data set as " + json.dumps(mock_campaign_list)
        self.ctx.send.assert_called_once_with(expected_response)


    async def test_setPlayedSeconds(self):
        initial_campaign_data = [
            {"Campaign name": "Test Campaign", "Expected length": 1.0, "Seconds of plot play": 0} # 1 hour = 3600s
        ]
        # Ensure getCmpnDataForWrite returns a mutable copy if the test modifies it
        self.data_mock.cmpnHelp.getCmpnDataForWrite.return_value = [dict(item) for item in initial_campaign_data]
        self.data_mock.progHelp.getTForWrite.return_value = 0.0 # Initial T

        await self.cog.setPlayedSeconds.callback(self.cog, self.ctx, 1800) # 1800 seconds

        self.data_mock.cmpnHelp.getCmpnDataForWrite.assert_called_once_with("TestUser")

        updated_campaign_data = initial_campaign_data # The callback modifies the list in place
        updated_campaign_data[0]["Seconds of plot play"] = 1800

        self.data_mock.cmpnHelp.setCmpnData.assert_called_once_with("TestUser", updated_campaign_data)

        self.data_mock.progHelp.getTForWrite.assert_called_once_with("TestUser")
        # Expected T = 1800 / (1.0 * 60 * 60) = 1800 / 3600 = 0.5
        self.data_mock.progHelp.setT.assert_called_once_with("TestUser", 0.5)

        expected_response = "Current campaign played seconds set to: 1800"
        self.ctx.send.assert_called_once_with(expected_response)

if __name__ == '__main__':
    # Need to run with python -m unittest discover -s tests/campaign_help_tests
    # or python -m unittest tests.campaign_help_tests.test_campaign_help
    # For asyncio tests in older python versions, a specific test runner might be needed if run directly.
    unittest.main()
