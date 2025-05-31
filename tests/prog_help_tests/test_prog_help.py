import unittest
from unittest.mock import AsyncMock, Mock, patch
import discord
from discord.ext import commands

# Assuming the cog is in a directory named 'cogs' at the root of the project
# and dataHelp is in a directory named 'data'
import sys
# sys.path.append('../..')  # Adjust this if your directory structure is different # Removed
import progressivenessHelpers  # Import the cog
import dataHelpers # Import dataHelpers, will mock it.

class TestProgHelp(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = AsyncMock(spec=commands.Bot) # Changed to AsyncMock for consistency
        # Create a mock for the dataHelp dependency
        self.data_mock = Mock() # Top level mock for dataHelp
        self.data_mock.progHelp = AsyncMock() # Mock for the progHelp attribute

        self.cog = progressivenessHelpers.ProgHelp(self.bot, self.data_mock)
        self.ctx = AsyncMock(spec=commands.Context) # Corrected spec
        self.ctx.message = Mock()
        self.ctx.message.author = Mock()
        self.ctx.message.author.name = "TestUser"
        self.ctx.send = AsyncMock()

    @patch('progressivenessHelpers.PlotGrowthCurve') # Mocking helper functions in the cog's module
    @patch('progressivenessHelpers.GraphProgressivenessRoll')
    @patch('progressivenessHelpers.getAlphaAndBeta', return_value=(1.0, 1.0))
    @patch('discord.File')
    async def test_setT(self, mock_discord_file, mock_get_alpha_beta, mock_graph_prog_roll, mock_plot_growth_curve):
        self.data_mock.progHelp.getTForWrite.return_value = 0.0 # Old T value
        self.data_mock.progHelp.setT = AsyncMock() # Mock the setT method

        await self.cog.setT.callback(self.cog, self.ctx, "0.5") # Pass t as string, as it comes from command

        mock_plot_growth_curve.assert_called_once_with(0.5)
        mock_graph_prog_roll.assert_called_once_with(0.5)
        mock_get_alpha_beta.assert_called_once_with(0.5)

        self.data_mock.progHelp.setT.assert_called_once_with("TestUser", 0.5)

        # Check ctx.send calls. There are multiple.
        self.assertEqual(self.ctx.send.call_count, 5)
        self.ctx.send.assert_any_call(file=mock_discord_file.return_value) # Check for file sends
        self.ctx.send.assert_any_call("t = 0.5 | alpha = 1.0 | beta = 1.0")


    @patch('progressivenessHelpers.PlotGrowthCurve')
    @patch('progressivenessHelpers.getAlphaAndBeta', return_value=(1.0, 1.0))
    @patch('discord.File')
    async def test_getT(self, mock_discord_file, mock_get_alpha_beta, mock_plot_growth_curve):
        self.data_mock.progHelp.getTForNoWrite.return_value = 0.5

        await self.cog.getT.callback(self.cog, self.ctx)

        mock_plot_growth_curve.assert_called_once_with(0.5)
        mock_get_alpha_beta.assert_called_once_with(0.5)
        self.data_mock.progHelp.getTForNoWrite.assert_called_once()

        self.assertEqual(self.ctx.send.call_count, 2)
        self.ctx.send.assert_any_call(file=mock_discord_file.return_value)
        self.ctx.send.assert_any_call("t = 0.5 | alpha = 1.0 | beta = 1.0")


    @patch('progressivenessHelpers.GraphProgressivenessRoll')
    @patch('discord.File')
    async def test_printDistribution(self, mock_discord_file, mock_graph_prog_roll):
        self.data_mock.progHelp.getTForNoWrite.return_value = 0.3

        await self.cog.printDistribution.callback(self.cog, self.ctx)

        self.data_mock.progHelp.getTForNoWrite.assert_called_once()
        mock_graph_prog_roll.assert_called_once_with(0.3)
        mock_discord_file.assert_called_once_with("distribution.png")

        self.assertEqual(self.ctx.send.call_count, 2)
        self.ctx.send.assert_any_call(file=mock_discord_file.return_value)
        self.ctx.send.assert_any_call("t = 0.3")


    @patch('progressivenessHelpers.RollProgressiveness', return_value=5.0) # Mock the actual roll function
    async def test_rollProg(self, mock_roll_progressiveness):
        self.data_mock.progHelp.getTForNoWrite.return_value = 0.3
        self.data_mock.progHelp.incrementNumProgRolls = AsyncMock()

        await self.cog.rollProg.callback(self.cog, self.ctx)

        self.data_mock.progHelp.getTForNoWrite.assert_called_once()
        mock_roll_progressiveness.assert_called_once_with(0.3)
        self.data_mock.progHelp.incrementNumProgRolls.assert_called_once()
        self.ctx.send.assert_called_once_with("5.0 - Very Counter-Progressive")


    @patch('numpy.random.randint', return_value=3) # Mock the random roll for alignment
    async def test_rollAlign(self, mock_randint):
        await self.cog.rollAlign.callback(self.cog, self.ctx)
        mock_randint.assert_called_once_with(1,20)
        self.ctx.send.assert_called_once_with("3 - Bad")

if __name__ == '__main__':
    unittest.main()
