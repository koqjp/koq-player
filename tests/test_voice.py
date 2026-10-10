from unittest.mock import MagicMock, Mock, patch

import pytest
import yt_dlp

from koq.player.cogs.voice import AudioCog
from koq.player.queue import PlayingQueue


@pytest.fixture
def cog(mock_bot):
    return AudioCog(mock_bot)


def _ydl_ctx(instance: MagicMock) -> MagicMock:
    """Wrap a mock ydl instance so it works as a context manager."""
    cm = MagicMock()
    cm.__enter__ = Mock(return_value=instance)
    cm.__exit__ = Mock(return_value=False)
    return cm


class TestPauseCommand:
    async def test_pause_when_playing(self, cog, mock_ctx, mock_voice_client):
        mock_voice_client.is_playing.return_value = True
        with patch("discord.utils.get", return_value=mock_voice_client):
            await cog.pause.callback(cog, mock_ctx)
        mock_voice_client.pause.assert_called_once()
        mock_ctx.send.assert_called_with("Music paused.")

    async def test_pause_when_not_playing(self, cog, mock_ctx, mock_voice_client):
        mock_voice_client.is_playing.return_value = False
        with patch("discord.utils.get", return_value=mock_voice_client):
            await cog.pause.callback(cog, mock_ctx)
        mock_voice_client.pause.assert_not_called()
        mock_ctx.send.assert_called_with("No song is currently playing.")


class TestResumeCommand:
    async def test_resume_when_paused(self, cog, mock_ctx, mock_voice_client):
        mock_voice_client.is_paused.return_value = True
        with patch("discord.utils.get", return_value=mock_voice_client):
            await cog.resume.callback(cog, mock_ctx)
        mock_voice_client.resume.assert_called_once()
        mock_ctx.send.assert_called_with("Music resumed.")

    async def test_resume_when_not_paused(self, cog, mock_ctx, mock_voice_client):
        mock_voice_client.is_paused.return_value = False
        with patch("discord.utils.get", return_value=mock_voice_client):
            await cog.resume.callback(cog, mock_ctx)
        mock_voice_client.resume.assert_not_called()
        mock_ctx.send.assert_called_with("No song is currently paused.")


class TestSkipCommand:
    async def test_skip_when_playing(self, cog, mock_ctx, mock_voice_client):
        mock_voice_client.is_playing.return_value = True
        with patch("discord.utils.get", return_value=mock_voice_client):
            await cog.skip.callback(cog, mock_ctx)
        mock_voice_client.stop.assert_called_once()

    async def test_skip_when_not_playing(self, cog, mock_ctx, mock_voice_client):
        mock_voice_client.is_playing.return_value = False
        with patch("discord.utils.get", return_value=mock_voice_client):
            await cog.skip.callback(cog, mock_ctx)
        mock_voice_client.stop.assert_not_called()
        mock_ctx.send.assert_called_with("No song is currently playing.")


class TestStopCommand:
    async def test_stop_clears_queue_and_disconnects(self, cog, mock_ctx, mock_voice_client):
        guild_id = mock_ctx.guild.id
        cog.queues[guild_id] = PlayingQueue()
        cog.queues[guild_id].append("url", "Title", "user")
        mock_voice_client.is_playing.return_value = True

        with patch("discord.utils.get", return_value=mock_voice_client):
            await cog.stop.callback(cog, mock_ctx)

        assert guild_id not in cog.queues
        mock_voice_client.stop.assert_called_once()
        mock_voice_client.disconnect.assert_called_once()


class TestQueueCommand:
    async def test_queue_empty(self, cog, mock_ctx):
        await cog.queue.callback(cog, mock_ctx)
        mock_ctx.send.assert_called_once_with("No songs in queue.")

    async def test_queue_with_songs(self, cog, mock_ctx):
        guild_id = mock_ctx.guild.id
        cog.queues[guild_id] = PlayingQueue()
        cog.queues[guild_id].append("url1", "Song 1", "user1")
        cog.queues[guild_id].append("url2", "Song 2", "user2")

        await cog.queue.callback(cog, mock_ctx)

        sent = mock_ctx.send.call_args[0][0]
        assert "Song 1" in sent
        assert "Song 2" in sent


class TestVolumeCommand:
    async def test_volume_valid(self, cog, mock_ctx):
        mock_ctx.voice_client = Mock()
        mock_ctx.voice_client.is_connected.return_value = True
        mock_ctx.voice_client.source = Mock()

        await cog.volume.callback(cog, mock_ctx, "0.5")

        assert mock_ctx.voice_client.source.volume == 0.5
        mock_ctx.send.assert_called_with("Volume set to 0.5")

    async def test_volume_out_of_range(self, cog, mock_ctx):
        mock_ctx.voice_client = Mock()
        mock_ctx.voice_client.is_connected.return_value = True

        await cog.volume.callback(cog, mock_ctx, "1.5")

        mock_ctx.send.assert_called_with("Volume must be between 0 and 1.")

    async def test_volume_not_connected(self, cog, mock_ctx):
        mock_ctx.voice_client = None

        await cog.volume.callback(cog, mock_ctx, "0.5")

        mock_ctx.send.assert_called_with("Not connected to a voice channel.")


class TestGeneralHandler:
    async def test_download_error_returns_none(self, cog, mock_ctx):
        ydl = MagicMock()
        ydl.extract_info.side_effect = yt_dlp.DownloadError("bad url")

        with patch("yt_dlp.YoutubeDL", return_value=_ydl_ctx(ydl)):
            title, url = await cog.generalHandler(mock_ctx, "http://invalid.example.com")

        assert title is None
        assert url is None
        assert "❌ Invalid URL." in mock_ctx.send.call_args[0][0]

    async def test_cached_file_skips_download(self, cog, mock_ctx):
        ydl = MagicMock()
        ydl.extract_info.return_value = {"title": "Test Song"}
        ydl.prepare_filename.return_value = "tmp/Test Song.m4a"

        with (
            patch("yt_dlp.YoutubeDL", return_value=_ydl_ctx(ydl)),
            patch("os.path.exists", return_value=True),
        ):
            title, filename = await cog.generalHandler(mock_ctx, "http://youtube.com/watch?v=x")

        assert title == "Test Song"
        assert filename == "tmp/Test Song.m4a"
        ydl.extract_info.assert_called_once_with("http://youtube.com/watch?v=x", download=False)

    async def test_downloads_when_not_cached(self, cog, mock_ctx):
        ydl = MagicMock()
        ydl.extract_info.return_value = {"title": "New Song"}
        ydl.prepare_filename.return_value = "tmp/New Song.m4a"

        with (
            patch("yt_dlp.YoutubeDL", return_value=_ydl_ctx(ydl)),
            patch("os.path.exists", return_value=False),
        ):
            title, _ = await cog.generalHandler(mock_ctx, "http://youtube.com/watch?v=y")

        assert title == "New Song"
        assert ydl.extract_info.call_count == 2


class TestStorageServerHandler:
    async def test_non_storage_url_returns_none(self, cog, mock_ctx):
        title, url = await cog.storageServerHandler(mock_ctx, "http://other.example.com/file")
        assert title is None
        assert url is None
        mock_ctx.send.assert_called_with("Invalid URL.")

    async def test_valid_storage_url(self, cog, mock_ctx):
        ydl = MagicMock()

        with (
            patch("yt_dlp.YoutubeDL", return_value=_ydl_ctx(ydl)),
            patch("koq.player.cogs.voice.os.rename"),
        ):
            title, filepath = await cog.storageServerHandler(
                mock_ctx, "https://storage.koq.jp/s/abc123"
            )

        assert title == "abc123.m4a"
        assert filepath == "tmp/abc123.m4a"

    async def test_storage_download_error(self, cog, mock_ctx):
        ydl = MagicMock()
        ydl.extract_info.side_effect = yt_dlp.DownloadError("fail")

        with patch("yt_dlp.YoutubeDL", return_value=_ydl_ctx(ydl)):
            title, url = await cog.storageServerHandler(mock_ctx, "https://storage.koq.jp/s/abc123")

        assert title is None
        assert url is None
        assert "❌ Invalid URL." in mock_ctx.send.call_args[0][0]
