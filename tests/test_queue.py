"""Tests for the PlayingQueue and PlayingQueueItem classes."""

import pytest

from koq.player.queue import PlayingQueue, PlayingQueueItem


class TestPlayingQueueItem:
    """Test cases for PlayingQueueItem class."""

    def test_init(self):
        """Test PlayingQueueItem initialization."""
        item = PlayingQueueItem(
            url="http://example.com/song.mp3", title="Test Song", requester="test_user"
        )

        assert item.url == "http://example.com/song.mp3"
        assert item.title == "Test Song"
        assert item.requester == "test_user"

    def test_str(self):
        """Test PlayingQueueItem string representation."""
        item = PlayingQueueItem(
            url="http://example.com/song.mp3", title="Test Song", requester="test_user"
        )

        expected = "Test Song - Requested by test_user"
        assert str(item) == expected


class TestPlayingQueue:
    """Test cases for PlayingQueue class."""

    def test_init(self):
        """Test PlayingQueue initialization."""
        queue = PlayingQueue()
        assert len(queue) == 0
        assert queue.items == []

    def test_append(self):
        """Test adding items to the queue."""
        queue = PlayingQueue()
        queue.append(url="http://example.com/song.mp3", title="Test Song", requester="test_user")

        assert len(queue) == 1
        assert queue.items[0].title == "Test Song"
        assert queue.items[0].url == "http://example.com/song.mp3"
        assert queue.items[0].requester == "test_user"

    def test_pop(self):
        """Test removing items from the queue."""
        queue = PlayingQueue()
        queue.append("url1", "Song 1", "user1")
        queue.append("url2", "Song 2", "user2")

        assert len(queue) == 2

        item = queue.pop()
        assert item.title == "Song 1"
        assert len(queue) == 1

        item = queue.pop()
        assert item.title == "Song 2"
        assert len(queue) == 0

    def test_len(self):
        """Test queue length."""
        queue = PlayingQueue()
        assert len(queue) == 0

        queue.append("url1", "Song 1", "user1")
        assert len(queue) == 1

        queue.append("url2", "Song 2", "user2")
        assert len(queue) == 2

    def test_str(self):
        """Test queue string representation."""
        queue = PlayingQueue()
        assert str(queue) == ""

        queue.append("url1", "Song 1", "user1")
        queue.append("url2", "Song 2", "user2")

        expected = "Song 1 - Requested by user1\nSong 2 - Requested by user2"
        assert str(queue) == expected

    def test_empty_queue_pop(self):
        """Test popping from empty queue raises IndexError."""
        queue = PlayingQueue()
        with pytest.raises(IndexError):
            queue.pop()
