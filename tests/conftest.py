"""Test configuration for pytest."""

from unittest.mock import AsyncMock, Mock

import discord
import pytest
from discord.ext import commands


@pytest.fixture
def mock_bot():
    """Create a mock Discord bot for testing."""
    bot = Mock(spec=commands.Bot)
    bot.voice_clients = []
    return bot


@pytest.fixture
def mock_ctx():
    """Create a mock Discord context for testing."""
    ctx = Mock(spec=commands.Context)
    ctx.guild = Mock()
    ctx.guild.id = 12345
    ctx.author = Mock()
    ctx.author.name = "test_user"
    ctx.author.voice = Mock()
    ctx.author.voice.channel = Mock()
    ctx.send = AsyncMock()
    ctx.message = Mock()
    ctx.message.add_reaction = AsyncMock()
    return ctx


@pytest.fixture
def mock_voice_client():
    """Create a mock Discord voice client for testing."""
    voice_client = Mock(spec=discord.VoiceClient)
    voice_client.is_connected.return_value = True
    voice_client.is_playing.return_value = False
    voice_client.is_paused.return_value = False
    voice_client.play = Mock()
    voice_client.pause = Mock()
    voice_client.resume = Mock()
    voice_client.stop = Mock()
    voice_client.disconnect = AsyncMock()
    return voice_client
