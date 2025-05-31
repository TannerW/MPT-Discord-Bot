import unittest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import discord
from discord.ext import commands
import json
import datetime as datetime_module
import pytz
import copy # Import copy for deepcopy

# Adjust path to import cogs and dataHelpers
import sys
sys.path.append('../..')
import adventuringDayHelpers
from dataDefaults import advenDayDataDefault, advenDayAdjExpPerChar # For calculations and defaults

# Global for bot.wait_for mock responses
mock_user_messages_adven_day = []

class TestAdvenDayHelp(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.bot = AsyncMock(spec=commands.Bot)
        self.data_mock = Mock() # Top-level mock for dataHelp
        self.data_mock.cmpnHelp = AsyncMock()
        self.data_mock.advenDayHelp = AsyncMock()
        # self.data_mock.sessHelp = AsyncMock() # Not directly used by AdvenDayHelp

        self.cog = adventuringDayHelpers.AdvenDayHelp(self.bot, self.data_mock)

        self.ctx = AsyncMock(spec=commands.Context)
        self.ctx.message = Mock()
        self.ctx.message.author = Mock(spec=discord.Member)
        self.ctx.message.author.name = "TestUser"
        self.ctx.author = self.ctx.message.author
        self.ctx.channel = Mock(spec=discord.TextChannel)
        self.ctx.send = AsyncMock()

        global mock_user_messages_adven_day
        mock_user_messages_adven_day = []

        async def mock_wait_for_adven_day(event, check):
            self.assertEqual(event, 'message')
            if mock_user_messages_adven_day:
                msg = mock_user_messages_adven_day.pop(0)
                if check(msg): # Ensure the check passes for the mocked message
                    return msg
            raise asyncio.TimeoutError("No message for adven_day test")
        self.bot.wait_for = mock_wait_for_adven_day

        # Ensure advenDayAdjExpPerChar is available in the adventuringDayHelpers module's scope
        # If it's directly used from dataDefaults, this might not be strictly necessary to patch
        # but good for explicit test control if it were ever to change.
        # For now, assuming direct import from dataDefaults works.
        adventuringDayHelpers.advenDayAdjExpPerChar = advenDayAdjExpPerChar


    @patch('adventuringDayHelpers.datetime', new_callable=MagicMock)
    async def test_startNewAdvenDay_single_pc(self, mock_datetime_class):
        adventuringDayHelpers.ttsEnabled = False # Set ttsEnabled directly

        # Mock return values
        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.return_value = [{"Campaign name": "Test Campaign DMA"}]
        self.data_mock.advenDayHelp.getAdvenDayDataForWrite.return_value = [] # No prior adven day data

        # Configure datetime.now() mock
        mock_now_val = datetime_module.datetime(2023, 10, 26, 10, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
        mock_datetime_class.now.return_value = mock_now_val

        # Prepare mock user responses for bot.wait_for
        global mock_user_messages_adven_day
        num_chars_msg = Mock(spec=discord.Message, content="1", author=self.ctx.author, channel=self.ctx.channel)
        char1_name_msg = Mock(spec=discord.Message, content="Gandalf", author=self.ctx.author, channel=self.ctx.channel)
        char1_lvl_msg = Mock(spec=discord.Message, content="5", author=self.ctx.author, channel=self.ctx.channel)
        mock_user_messages_adven_day = [num_chars_msg, char1_name_msg, char1_lvl_msg]

        await self.cog.startNewAdvenDay.callback(self.cog, self.ctx)

        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.assert_called_once_with("TestUser")
        self.data_mock.advenDayHelp.getAdvenDayDataForWrite.assert_called_once_with("TestUser")

        expected_adven_day_item = copy.deepcopy(advenDayDataDefault) # Use deepcopy
        expected_adven_day_item["Campaign name"] = "Test Campaign DMA"
        expected_adven_day_item["AdvenDay start time"] = mock_now_val.timestamp()
        expected_adven_day_item["PCs"] = {"Gandalf": 5}
        expected_adven_day_item["Experience goal"] = advenDayAdjExpPerChar[5] # Gandalf lvl 5

        self.data_mock.advenDayHelp.setAdvenDayData.assert_called_once_with("TestUser", [expected_adven_day_item])

        self.assertEqual(self.ctx.send.call_count, 6) # Initial data, num_chars_prompt, name_prompt, lvl_prompt, final data, success message
        self.ctx.send.assert_any_call("Current session data []")
        self.ctx.send.assert_any_call("How many characters will be participating in this adventuring day?", tts=False)
        self.ctx.send.assert_any_call("What is the name of character 1?", tts=False)
        self.ctx.send.assert_any_call("What is Gandalf's level?", tts=False)
        self.ctx.send.assert_any_call("Current session data " + json.dumps(expected_adven_day_item))
        self.ctx.send.assert_any_call("Adventuring day started! Enjoy your adventuring!!", tts=False)


    @patch('adventuringDayHelpers.datetime', new_callable=MagicMock)
    async def test_startNewAdvenDay_multiple_pcs(self, mock_datetime_class):
        adventuringDayHelpers.ttsEnabled = False

        self.data_mock.cmpnHelp.getCmpnDataForNoWrite.return_value = [{"Campaign name": "Group Quest"}]

        # 1. Define what the very first item in existing_data will be
        item1_initial_state = copy.deepcopy(advenDayDataDefault)
        # Customize if default campaign name for this item needs to be different, but for this test it's okay
        # item1_initial_state["Campaign name"] = "Some other campaign"

        # 2. This is the list instance the cog will receive and modify
        list_for_cog_to_modify = [item1_initial_state]
        self.data_mock.advenDayHelp.getAdvenDayDataForWrite.return_value = list_for_cog_to_modify

        mock_now_val = datetime_module.datetime(2023, 10, 27, 11, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
        mock_datetime_class.now.return_value = mock_now_val

        global mock_user_messages_adven_day
        num_chars_msg = Mock(spec=discord.Message, content="2", author=self.ctx.author, channel=self.ctx.channel)
        char1_name_msg = Mock(spec=discord.Message, content="Aragorn", author=self.ctx.author, channel=self.ctx.channel)
        char1_lvl_msg = Mock(spec=discord.Message, content="7", author=self.ctx.author, channel=self.ctx.channel)
        char2_name_msg = Mock(spec=discord.Message, content="Legolas", author=self.ctx.author, channel=self.ctx.channel)
        char2_lvl_msg = Mock(spec=discord.Message, content="6", author=self.ctx.author, channel=self.ctx.channel)
        mock_user_messages_adven_day = [num_chars_msg, char1_name_msg, char1_lvl_msg, char2_name_msg, char2_lvl_msg]

        # 3. Define what the new item added by the cog should look like
        item2_expected_addition = copy.deepcopy(advenDayDataDefault)
        item2_expected_addition["Campaign name"] = "Group Quest"
        item2_expected_addition["AdvenDay start time"] = mock_now_val.timestamp()
        item2_expected_addition["PCs"] = {"Aragorn": 7, "Legolas": 6}
        item2_expected_addition["Experience goal"] = advenDayAdjExpPerChar[7] + advenDayAdjExpPerChar[6]

        # 4. This is the final list structure we expect to be passed to setAdvenDayData
        expected_final_list = [item1_initial_state, item2_expected_addition]

        await self.cog.startNewAdvenDay.callback(self.cog, self.ctx)

        self.data_mock.advenDayHelp.setAdvenDayData.assert_called_once_with("TestUser", expected_final_list)

        self.assertEqual(self.ctx.send.call_count, 8) # Initial data, num_chars, 2x(name, lvl), final data, success
        # The check for "Current session data" is now handled by checking all_send_calls:

        # Check the important calls
        all_send_calls = [call_args[0][0] for call_args in self.ctx.send.call_args_list]
        self.assertIn("Current session data " + json.dumps([item1_initial_state]), all_send_calls)
        self.assertIn("Adventuring day started! Enjoy your adventuring!!", all_send_calls)


if __name__ == '__main__':
    unittest.main()
