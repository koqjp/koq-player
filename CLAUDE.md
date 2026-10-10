# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync --all-extras --dev   # install deps
uv run python run.py         # run bot locally
uv run pytest                # full test suite
uv run pytest tests/test_queue.py::TestPlayingQueue::test_pop  # single test
uv run pytest -m "not slow"  # skip slow tests
uv run ruff check .          # lint
uv run ruff format .         # format
docker compose up --build    # containerized run
```

FFmpeg must be installed on the host for audio playback (included in Docker image).

## Configuration

Dynaconf loads `settings.toml` then `.secrets.toml`. Required keys: `token`, `client_id`. Optional: `guild_id` (if set, slash commands sync to that guild only instead of globally).

For Docker/CI, use env vars: `DYNACONF_TOKEN`, `DYNACONF_CLIENT_ID`.

## Architecture

`run.py` — entrypoint. Creates `KoqBot` (subclass of `commands.Bot`), loads cogs listed in `INITIAL_EXTENSIONS`, syncs slash commands, then starts the bot.

`koq/player/config.py` — thin Dynaconf wrapper, imports `settings` used everywhere.

`koq/player/queue.py` — `PlayingQueue` (FIFO list of `PlayingQueueItem`). No async, pure data.

`koq/player/cogs/voice.py` (`AudioCog`) — core music logic. Maintains `self.queues: dict[int, PlayingQueue]` keyed by guild ID. Three URL handlers:
- Local file path → played directly
- `storage.koq.jp` URLs → `storageServerHandler` (appends `/download`, renames output to `tmp/<token>.m4a`)
- Everything else → `generalHandler` (yt-dlp downloads to `tmp/`, caches by filename so re-queuing same URL skips download)

Audio is downloaded to `tmp/` as `.m4a` via yt-dlp + FFmpegExtractAudio, then played via `discord.FFmpegPCMAudio` wrapped in `PCMVolumeTransformer`. `play_next` is recursive and polls `is_playing()`/`is_paused()` with 1-second sleeps.

`koq/player/util/http.py` — `HttpHeadGetter` static helpers for HEAD requests (content-length, content-type). Currently unused by cogs.

## Adding a new cog

1. Create `koq/player/cogs/<name>.py` with a `Cog` subclass and `async def setup(bot)`.
2. Add the cog name string to `INITIAL_EXTENSIONS` in `run.py`.

## Commit style

Conventional commits: `fix:`, `feat:`, `chore:`, `build(deps):`. Semantic-release reads these to auto-bump versions and update `CHANGELOG.md`.
