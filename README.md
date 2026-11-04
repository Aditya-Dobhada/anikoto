# Anikoto

Fast anime downloader and desktop app for `anikoto.tv`, `anikoto.bz`, `anikoto.net`, and `anikoto.cz`.

---

## Windows Quick Start (No Python Required)

1. Go to **[Latest Releases](https://github.com/Aditya-Dobhada/anikoto/releases/latest)**.
2. Download **`anikoto-windows.zip`**.
3. Extract the zip file anywhere on your computer.
4. Double-click **`Anikoto.exe`** to open the app.

Paste the anime URL, choose Sub or Dub, set your episode range, and click **Start Download**.

---

## macOS and Linux Quick Start

### Option 1: Install with `uv` (Fastest)

```bash
uv tool install git+https://github.com/Aditya-Dobhada/anikoto.git
```

Run either the GUI or CLI:
```bash
anikoto --gui
anikoto "https://anikoto.cz/watch/one-piece-odmau" -a sub --range 14-14
```

### Option 2: Install with `pip`

```bash
pip install git+https://github.com/Aditya-Dobhada/anikoto.git
```

---

## Command Line Usage

Use the `anikoto` command to download episodes directly from the terminal.

### Download a Single Episode (with Subtitles)

```bash
anikoto "https://anikoto.cz/watch/one-piece-odmau" -p ~/Movies -a sub --range 14-14
```

### Download an Episode Range

```bash
anikoto "https://anikoto.cz/watch/solo-leveling-ilh08" -p ~/Anime -a sub --range 1-12
```

### Download Specific Episodes

```bash
anikoto "https://anikoto.cz/watch/frieren-beyond-journey-s-end-c6fbj" -p ~/Anime -a sub -e 1,3,7
```

### Download from a Specific Server (e.g. `vidstream-1`)

```bash
anikoto "https://anikoto.cz/watch/one-piece-odmau" -p ~/Movies -a sub --range 14-14 --source vidstream-1
```

### List Episodes Without Downloading

```bash
anikoto "https://anikoto.cz/watch/one-piece-odmau" --list
```

### Launch the Desktop GUI from Terminal

```bash
anikoto --gui
```

---

## Command Line Options

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
| `url` | | | Anime series or episode URL |
| `--gui` | | `False` | Launch desktop graphical interface |
| `--audio` | `-a` | `dub` | Audio version: `sub` (original + subtitles) or `dub` (English) |
| `--range` | `-r` | | Episode range (e.g. `1-12`, or `14-14` for episode 14 only) |
| `--episode` | `-e` | | Comma-separated episode list (e.g. `1,3,5`) |
| `--source` | `-s` | All | Specific server (e.g. `vidstream-1`, `hd-1`, `vidstream-2`) |
| `--quality` | `-q` | `1080` | Video resolution: `2160`, `1440`, `1080`, `720`, `480`, `360` |
| `--path` | `-p` | `./` | Destination directory |
| `--subtitles` | `-ss` | `True` | Download subtitles when available |
| `--subtitle-lang` | `-sl` | `English` | Filter subtitles by language name |
| `--downloader` | `-d` | `yt-dlp` | Download engine: `yt-dlp`, `ffmpeg`, or `N_m3u8DL-RE` |
| `--list` | | `False` | List all available episodes and exit |
| `--last` | | `False` | Download only the latest episode |
| `--debug` | | `False` | Print detailed logs |

---

## Subtitles

When downloading with `-a sub`, subtitle tracks are saved alongside the video file as `.vtt` with identical names:

```
One Piece E14 Luffy Back in Action! Miss Kaya's Desperate Resistance!.mp4
One Piece E14 Luffy Back in Action! Miss Kaya's Desperate Resistance!.en.vtt
```

Media players such as VLC, IINA, and MPV automatically load and display these subtitles.

To merge subtitles into the `.mp4` file as a soft-subtitle track:

```bash
ffmpeg -i "Episode.mp4" -i "Episode.en.vtt" -c copy -c:s mov_text "Episode-subbed.mp4"
```

---

## License

MIT
