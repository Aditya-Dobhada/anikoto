# 🌀 Anikoto Anime Downloader

A fast, clean anime downloader and desktop app for `anikoto.tv`, `anikoto.bz`, `anikoto.net`, and `anikoto.cz`.

Includes both a **modern graphical user interface (GUI)** for desktop users and a **full-featured CLI** for scripts and automation.

---

## Highlights

- **Desktop GUI:** Sleek dark-mode interface with URL auto-fetch, episode range pickers, progress bars, and one-click folder opening.
- **Portable Windows Executable:** Zero installation required on Windows—download and run directly.
- **Multiple Audio Tracks:** Seamless support for **Sub** (original audio + subtitles) and **Dub** (English).
- **Flexible Episode Selection:** Download individual episodes (`--range 14-14`), full seasons (`--range 1-24`), arbitrary lists (`-e 1,3,7`), or entire series.
- **Specific Server Selection:** Target generic providers (`vidstream`, `megaplay`, `hd`, `kiwi`, `vidcloud`, `vidplay`) or exact server channels (`vidstream-1`, `hd-1`, `vidstream-2`).
- **Subtitle Handling:** Automatically fetches WebVTT captions with matching filenames for instant playback in media players (IINA, VLC, MPV).
- **Quality Selector:** Choose stream bitrates from `360p` up to `2160p` (`1080p` default).
- **Fast Multithreaded Downloads:** Powered by `yt-dlp` with fragment concurrency.

---

## Desktop App (GUI)

Anikoto features a standalone desktop interface designed for easy, click-and-run usage without needing to type terminal commands.

### Windows (Zero Install)

1. Download `anikoto-windows.zip` from the latest [GitHub Releases](https://github.com/Aditya-Dobhada/anikoto/releases).
2. Extract the folder.
3. Double-click **`Anikoto-GUI.exe`**.

### Run via `uvx` (macOS, Windows, Linux)

If you have `uv` installed, launch the GUI instantly without cloning:

```bash
uvx --from git+https://github.com/Aditya-Dobhada/anikoto.git anikoto-gui
```

### Run from Source / Terminal

If installed locally, run:

```bash
anikoto-gui
```

*(Running `anikoto` without any arguments also automatically opens the GUI).*

---

## Quick Windows Setup (Non-Technical Guide)

If you are setting up a Windows PC and prefer a one-line installer:

1. Press the **Windows Key**, type **`powershell`**, and hit **Enter**.
2. Paste this command and press **Enter** (installs `uv` automatically):
   ```powershell
   irm https://astral.sh/uv/install.ps1 | iex
   ```
3. Restart PowerShell.
4. Launch the desktop app:
   ```powershell
   uvx --from git+https://github.com/Aditya-Dobhada/anikoto.git anikoto-gui
   ```
   Or download an episode directly:
   ```powershell
   uvx --from git+https://github.com/Aditya-Dobhada/anikoto.git anikoto "https://anikoto.cz/watch/one-piece-odmau" -p "$HOME\Videos" -a sub --range 14-14
   ```

---

## CLI Installation

### Recommended: Using `uv` / `uvx`

Run directly without installing into global system Python:

```bash
uvx --from git+https://github.com/Aditya-Dobhada/anikoto.git anikoto "https://anikoto.cz/watch/one-piece-odmau" -p ~/Movies -a sub --range 14-14
```

Or install persistently as a global CLI tool:

```bash
uv tool install git+https://github.com/Aditya-Dobhada/anikoto.git
```

### Using `pip`

```bash
python3 -m pip install git+https://github.com/Aditya-Dobhada/anikoto.git
```

---

## CLI Reference

```
usage: anikoto [-h] [--gui] [--version] [--debug]
               [--quality {2160,1440,1080,720,480,360}] [--audio {sub,dub}]
               [--downloader {yt-dlp,N_m3u8DL-RE,ffmpeg}] [--subtitles]
               [--list] [--last] [--subtitle-lang LANG] [--path PATH]
               [--source SOURCE] [--episode EPISODE] [--range RANGE]
               [url]
```

| Flag | Short | Default | Description |
|---|---|---|---|
| `url` | | *Optional if `--gui`* | Series or episode URL (e.g. `https://anikoto.cz/watch/one-piece-odmau`) |
| `--gui` | | `False` | Launch the graphical user interface |
| `--quality` | `-q` | `1080` | Video resolution: `2160`, `1440`, `1080`, `720`, `480`, `360` |
| `--audio` | `-a` | `dub` | Audio type: `sub` (original + subtitles) or `dub` (English) |
| `--range` | `-r` | None | Range of episodes (e.g. `1-10`, or `14-14` for only episode 14) |
| `--episode` | `-e` | None | Comma-separated list of episodes (e.g. `1,4,12`) |
| `--source` | `-s` | All | Specific server channel (e.g. `vidstream-1`, `hd-1`, `vidstream-2`) |
| `--subtitles` | `-ss` | `True` | Download subtitle track when available |
| `--subtitle-lang` | `-sl` | `English` | Subtitle language name filter |
| `--downloader` | `-d` | `yt-dlp` | Downloader engine: `yt-dlp`, `ffmpeg`, or `N_m3u8DL-RE` |
| `--path` | `-p` | `./` | Save folder path |
| `--list` | | `False` | Print available episodes and exit |
| `--last` | | `False` | Download only the newest episode |
| `--debug` | | `False` | Output detailed request & stream logging |

---

## Examples

### Download Single Episode (Subbed)

```bash
anikoto "https://anikoto.cz/watch/one-piece-odmau" -p ~/Movies -a sub --range 14-14
```

### Download Episode Range

```bash
anikoto "https://anikoto.cz/watch/solo-leveling-ilh08" -p ~/Anime -a sub --range 1-12
```

### Download from Specific Server (e.g. `vidstream-1`)

```bash
anikoto "https://anikoto.cz/watch/one-piece-odmau" -p ~/Movies -a sub --range 14-14 --source vidstream-1
```

### Download Specific Episodes

```bash
anikoto "https://anikoto.cz/watch/frieren-beyond-journey-s-end-c6fbj" -p ~/Anime -a sub -e 1,3,7
```

### List Episodes Without Downloading

```bash
anikoto "https://anikoto.cz/watch/one-piece-odmau" --list
```

---

## Subtitles & Player Notes

When `-ss` is enabled (default), subtitles are saved as standard `.vtt` files directly alongside the `.mp4` video with matching file names.

- **VLC, IINA, and MPV:** Automatically detect and show the `.vtt` subtitle file when playing the video.
- **Soft-Sub Muxing:** To package the `.vtt` file directly inside the `.mp4` container as a selectable subtitle track:
  ```bash
  ffmpeg -i "Episode.mp4" -i "Episode.en.vtt" -c copy -c:s mov_text "Episode (Subbed).mp4"
  ```
- **Hardsub Burning:** To permanently render subtitles into the video frames:
  ```bash
  ffmpeg -i "Episode.mp4" -vf "subtitles='Episode.en.vtt'" -c:a copy "Episode (Hardsub).mp4"
  ```

---

## License

Distributed under the [MIT License](LICENSE).
