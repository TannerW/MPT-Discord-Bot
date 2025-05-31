import unittest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import discord
from discord.ext import commands
import json
import datetime as datetime_module # This is the module datetime
import pytz

# Adjust path to import cogs and dataHelpers
import sys
sys.path.append('../..')
import sessionHelpers
# No direct import of dataHelpers needed if fully mocked via constructor
from dataDefaults import sessionDataDefault # For startNewSess test

# Global for bot.wait_for mock responses
mock_user_messages_session = []

class TestSessionHelp(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.bot = AsyncMock(spec=commands.Bot)
        self.data_mock = Mock() # Top-level mock for dataHelp
        self.data_mock.cmpnHelp = AsyncMock()
        self.data_mock.sessHelp = AsyncMock()
        # self.data_mock.progHelp = AsyncMock() # Not directly used by SessionHelp
        # self.data_mock.timerHelp = AsyncMock() # Not directly used by SessionHelp

        self.cog = sessionHelpers.SessionHelp(self.bot, self.data_mock)

        self.ctx = AsyncMock(spec=commands.Context)
        self.ctx.message = Mock()
        self.ctx.message.author = Mock(spec=discord.Member)
        self.ctx.message.author.name = "TestUser"
        self.ctx.author = self.ctx.message.author
        self.ctx.channel = Mock(spec=discord.TextChannel)
        self.ctx.send = AsyncMock()

        global mock_user_messages_session
        mock_user_messages_session = []

        async def mock_wait_for_session(event, check):
            self.assertEqual(event, 'message')
            if mock_user_messages_session:
                msg = mock_user_messages_session.pop(0)
                if check(msg):
                    return msg
            raise asyncio.TimeoutError("No message for session test")
        self.bot.wait_for = mock_wait_for_session

        # Mock for bot.get_cog("tTimer") and its methods
        self.mock_ttimer_cog = AsyncMock()
        self.mock_ttimer_cog.startTimer = AsyncMock()
        self.mock_ttimer_cog.stopTimer = AsyncMock()
        # self.mock_ttimer_cog.killTimers = AsyncMock() # Not used by these commands
        self.bot.get_cog.return_value = self.mock_ttimer_cog

    @patch('sessionHelpers.datetime', new_callable=MagicMock)
    async def test_startNewSess_first_session_for_campaign(self, mock_datetime_class):
        sessionHelpers.ttsEnabled = False # Set ttsEnabled directly

        # Mock return values
        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.return_value = [{"Campaign name": "Test Campaign"}]
        self.data_mock.sessHelp.getSessDataForWrite.return_value = [] # No prior session data at all

        # Configure datetime.now() mock
        mock_now_val = datetime_module.datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
        mock_datetime_class.now.return_value = mock_now_val

        await self.cog.startNewSess.callback(self.cog, self.ctx)

        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.assert_called_once_with("TestUser")
        self.data_mock.sessHelp.getSessDataForWrite.assert_called_once_with("TestUser")

        expected_session_item = sessionDataDefault.copy()
        expected_session_item["Campaign name"] = "Test Campaign"
        expected_session_item["Session number"] = 1
        expected_session_item["Session start time"] = mock_now_val.timestamp()
        expected_session_item["Timestamp of last activity"] = mock_now_val.timestamp()

        self.data_mock.sessHelp.setSessData.assert_called_once_with("TestUser", [expected_session_item])
        self.data_mock.sessHelp.setSessActive.assert_called_once_with("TestUser")

        self.bot.get_cog.assert_called_once_with("tTimer")
        self.mock_ttimer_cog.startTimer.assert_called_once_with(self.ctx)

        self.assertEqual(self.ctx.send.call_count, 3) # Initial data, new data, success message
        self.ctx.send.assert_any_call("Current session data []")
        self.ctx.send.assert_any_call("Current session data " + json.dumps(expected_session_item))
        self.ctx.send.assert_any_call("Session started! Enjoy your adventuring!!", tts=False)


    @patch('sessionHelpers.datetime', new_callable=MagicMock)
    async def test_startNewSess_with_previous_unfinished_session_and_end_it(self, mock_datetime_class):
        sessionHelpers.ttsEnabled = False

        mock_campaign_name = "Ongoing Campaign"
        mock_prev_session_unfinished = sessionDataDefault.copy()
        mock_prev_session_unfinished["Campaign name"] = mock_campaign_name
        mock_prev_session_unfinished["Session number"] = 1
        mock_prev_session_unfinished["Session start time"] = datetime_module.datetime(2023, 1, 1, 10, 0, 0).timestamp()
        mock_prev_session_unfinished["Session end time"] = 0 # Unfinished

        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.return_value = [{"Campaign name": mock_campaign_name}]
        # Return a list that will be modified by the cog
        self.data_mock.sessHelp.getSessDataForWrite.return_value = [dict(mock_prev_session_unfinished)]

        # Datetime mock setup
        dt_now_end_old_sess = datetime_module.datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
        dt_now_start_new_sess = datetime_module.datetime(2023, 1, 1, 12, 5, 0, tzinfo=pytz.timezone('US/Eastern'))
        # Configure mock_datetime_class.now to return values in sequence for multiple calls
        mock_datetime_class.now.side_effect = [dt_now_end_old_sess, dt_now_start_new_sess, dt_now_start_new_sess]


        global mock_user_messages_session
        ans_msg = Mock(spec=discord.Message, content="y", author=self.ctx.author, channel=self.ctx.channel)
        mock_user_messages_session = [ans_msg]

        await self.cog.startNewSess.callback(self.cog, self.ctx)

        # Check that old session was ended
        # The list passed to setSessData will contain the modified old session and the new session
        call_args_list = self.data_mock.sessHelp.setSessData.call_args[0][1]
        self.assertEqual(len(call_args_list), 2)
        ended_session = call_args_list[0]
        self.assertEqual(ended_session["Session end time"], dt_now_end_old_sess.timestamp())

        new_session_item = call_args_list[1]
        self.assertEqual(new_session_item["Session number"], 2)
        self.assertEqual(new_session_item["Session start time"], dt_now_start_new_sess.timestamp())
        self.assertEqual(new_session_item["Timestamp of last activity"], dt_now_start_new_sess.timestamp())

        self.bot.get_cog.assert_called_once_with("tTimer")
        self.mock_ttimer_cog.startTimer.assert_called_once_with(self.ctx)
        self.ctx.send.assert_any_call("Uh oh... it looks like the last session didnt end... would you like to end it now? [y/n]:")


    @patch('sessionHelpers.datetime', new_callable=MagicMock)
    async def test_endSess_active_session(self, mock_datetime_class):
        sessionHelpers.ttsEnabled = False

        mock_active_session = sessionDataDefault.copy()
        mock_active_session["Campaign name"] = "Test Campaign"
        mock_active_session["Session number"] = 1
        mock_active_session["Session start time"] = datetime_module.datetime(2023,1,1,10,0,0).timestamp()
        mock_active_session["Session end time"] = 0 # Active

        # Simulate getSessDataForWrite returning a list with one active session
        self.data_mock.sessHelp.getSessDataForWrite.return_value = [dict(mock_active_session)]

        mock_now_val = datetime_module.datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
        mock_datetime_class.now.return_value = mock_now_val

        await self.cog.endSess.callback(self.cog, self.ctx)

        self.data_mock.sessHelp.getSessDataForWrite.assert_called_once_with("TestUser")

        # Verify the session data passed to setSessData
        updated_sess_data_list = self.data_mock.sessHelp.setSessData.call_args[0][1]
        self.assertEqual(len(updated_sess_data_list), 1)
        updated_session = updated_sess_data_list[0]
        self.assertEqual(updated_session["Session end time"], mock_now_val.timestamp())
        self.assertEqual(updated_session["Timestamp of last activity"], mock_now_val.timestamp())

        self.data_mock.sessHelp.setSessInactive.assert_called_once_with("TestUser")
        self.bot.get_cog.assert_called_once_with("tTimer")
        self.mock_ttimer_cog.stopTimer.assert_called_once_with(self.ctx)
        self.ctx.send.assert_called_once_with("Session ended! I hope you enjoyed your adventuring!!", tts=False)


    async def test_endSess_no_active_session(self):
        sessionHelpers.ttsEnabled = False
        # Case 1: Last session already ended
        mock_ended_session = sessionDataDefault.copy()
        mock_ended_session["Session end time"] = datetime_module.datetime(2023,1,1,10,0,0).timestamp()
        self.data_mock.sessHelp.getSessDataForWrite.return_value = [mock_ended_session]

        await self.cog.endSess.callback(self.cog, self.ctx)
        self.ctx.send.assert_called_once_with("Uh oh... looks like the session was either never started or has already ended...", tts=False)
        self.data_mock.sessHelp.setSessData.assert_not_called() # Should not try to set data

        # Case 2: No session data at all
        self.ctx.send.reset_mock() # Reset for next assertion
        self.data_mock.sessHelp.getSessDataForWrite.return_value = None # or []

        await self.cog.endSess.callback(self.cog, self.ctx)
        self.ctx.send.assert_called_once_with("No session data...", tts=False)
        self.data_mock.sessHelp.setSessData.assert_called_once_with("TestUser", None) # It does call setSessData with the received value


    async def test_getSessData(self):
        mock_data = [{"session_id": 1, "details": "some details"}]
        self.data_mock.sessHelp.getSessDataForNoWrite.return_value = mock_data

        await self.cog.getSessData.callback(self.cog, self.ctx)

        self.data_mock.sessHelp.getSessDataForNoWrite.assert_called_once_with("TestUser")
        self.ctx.send.assert_called_once_with("Session data set as " + json.dumps(mock_data))

if __name__ == '__main__':
    unittest.main()
