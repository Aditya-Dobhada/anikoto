# 🌀 Anikoto Downloader

CLI tool to download anime from `anikoto.tv`, `anikoto.bz`, `anikoto.net`, and `anikoto.cz`.

---

## Features

- **Multi-domain support:** Works across `anikoto.tv`, `anikoto.bz`, `anikoto.net`, and `anikoto.cz`.
- **Quality options:** Select stream resolutions: `2160`, `1440`, `1080` (default), `720`, `480`, `360`.
- **Audio selection:** Choose `sub` (original Japanese audio with subtitles) or `dub` (English dub).
- **Flexible episode downloads:** Download single episodes, ranges (`--range 1-12`, `--range 14-14`), or comma-separated lists (`--episode 1,3,5`).
- **Server selection:** Target generic sources (`megaplay`, `vidstream`, `kiwi`, `vidcloud`, `vidplay`, `hd`) or specific server numbers (`vidstream-1`, `vidstream-2`, `hd-1`).
- **Subtitle downloads:** Automatic WebVTT subtitle detection and download (`-ss`) with language filtering (`-sl`).
- **Downloader backends:** Supports `yt-dlp` (default), `ffmpeg`, and `N_m3u8DL-RE`.

---

## Installation

### Using `uv` / `uvx` (Recommended)

Run directly without manual installation:

```bash
uvx anikoto "https://anikoto.cz/watch/one-piece-odmau" -p ~/Movies -a sub --range 14-14
```

Or install as a persistent CLI tool:

```bash
uv tool install anikoto
```

### Using `pip`

Install from PyPI:

```bash
python3 -m pip install anikoto
```

Install latest development version from GitHub:

```bash
python3 -m pip install git+https://github.com/Aditya-Dobhada/anikoto.git
```

---

## CLI Reference

```
usage: anikoto [-h] [--version] [--debug]
               [--quality {2160,1440,1080,720,480,360}] [--audio {sub,dub}]
               [--downloader {yt-dlp,N_m3u8DL-RE,ffmpeg}] [--subtitles]
               [--list] [--last] [--subtitle-lang LANG] [--path PATH]
               [--source SOURCE] [--episode EPISODE] [--range RANGE]
               url
```

| Flag | Short | Default | Description |
|---|---|---|---|
| `url` | | *Required* | Episode or series URL (e.g. `https://anikoto.cz/watch/one-piece-odmau`) |
| `--quality` | `-q` | `1080` | Video resolution: `2160`, `1440`, `1080`, `720`, `480`, `360` |
| `--audio` | `-a` | `dub` | Audio type: `sub` or `dub` |
| `--range` | `-r` | None | Range of episodes to download (e.g. `1-10`, or `14-14` for a single episode) |
| `--episode` | `-e` | None | Comma-separated list of episode numbers (e.g. `1,4,12`) |
| `--last` | | `False` | Download only the latest episode |
| `--list` | | `False` | List available episodes and exit |
| `--source` | `-s` | All | Specific server or comma-separated servers (e.g. `vidstream-1`, `hd-1`, `megaplay`) |
| `--subtitles` | `-ss` | `True` | Download subtitles when available |
| `--subtitle-lang` | `-sl` | `English` | Subtitle language name filter |
| `--downloader` | `-d` | `yt-dlp` | Download backend: `yt-dlp`, `ffmpeg`, or `N_m3u8DL-RE` |
| `--path` | `-p` | `./` | Directory where downloaded episodes are saved |
| `--debug` | | `False` | Print verbose debug information |
| `--version` | `-v` | | Show program version |

---

## Examples

### Download a specific episode (Subtitled)

```bash
anikoto "https://anikoto.cz/watch/one-piece-odmau" -p ~/Movies -a sub --range 14-14
```

### Download an episode range

```bash
anikoto "https://anikoto.cz/watch/solo-leveling-ilh08" -p ~/Anime -a sub --range 1-5
```

### Download specific server (e.g. `vidstream-1` or `hd-1`)

```bash
anikoto "https://anikoto.cz/watch/one-piece-odmau" -p ~/Movies -a sub --range 14-14 --source vidstream-1
```

### Download specific episode numbers

```bash
anikoto "https://anikoto.cz/watch/frieren-beyond-journey-s-end-c6fbj" -p ~/Anime -a sub -e 1,3,7
```

### List available episodes without downloading

```bash
anikoto "https://anikoto.cz/watch/one-piece-odmau" --list
```

---

## Subtitles

When `-ss` is enabled (default), subtitles are saved as standard `.vtt` files alongside the `.mp4` video with matching basenames. Most media players (VLC, IINA, MPV) automatically load these subtitles on playback.

### Mux Subtitles into a Single File

To embed the `.vtt` subtitle into the video container as a selectable soft-subtitle track:

```bash
ffmpeg -i "Episode.mp4" -i "Episode.en.vtt" -c copy -c:s mov_text "Episode (Subbed).mp4"
```

### Burn Subtitles In (Hardsub)

To permanently burn the subtitles directly into the video frames:

```bash
ffmpeg -i "Episode.mp4" -vf "subtitles='Episode.en.vtt'" -c:a copy "Episode (Hardsub).mp4"
```

---

## License

Distributed under the [MIT License](LICENSE).
