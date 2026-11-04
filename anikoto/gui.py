"""
Anikoto GUI - Graphical User Interface for Anikoto Downloader
Modern desktop UI built with CustomTkinter for non-technical and everyday users.
"""

import os
import sys
import threading
import queue
import platform
import subprocess
from urllib.parse import urlparse
import logging

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    HAS_CUSTOMTKINTER = True
except ImportError:
    HAS_CUSTOMTKINTER = False
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

from anikoto.anikoto import clean_name, configure_logging


def get_default_save_dir():
    system = platform.system()
    if system == "Windows":
        videos = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Videos")
        if os.path.exists(videos):
            return videos
    elif system == "Darwin":
        movies = os.path.expanduser("~/Movies")
        if os.path.exists(movies):
            return movies
    else:
        videos = os.path.expanduser("~/Videos")
        if os.path.exists(videos):
            return videos
    return os.path.expanduser("~/Downloads")


class AnikotoGUI:
    def __init__(self):
        if not HAS_CUSTOMTKINTER:
            self._run_fallback_notice()
            return

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Anikoto Anime Downloader")
        self.root.geometry("860x780")
        self.root.minsize(780, 680)

        # Set icon if exists
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.anime_info = None
        self.is_downloading = False
        self.cancel_requested = False
        self.log_queue = queue.Queue()

        self._build_ui()
        self._start_log_listener()

    def _run_fallback_notice(self):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Missing Dependencies",
            "CustomTkinter is required to run the Anikoto GUI.\n\n"
            "Install it using:\n  pip install customtkinter"
        )
        sys.exit(1)

    def _build_ui(self):
        # Main scrollable canvas / container
        self.main_container = ctk.CTkScrollableFrame(self.root, corner_radius=0)
        self.main_container.pack(fill="both", expand=True, padx=16, pady=16)

        # Header
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 12))

        title_label = ctk.CTkLabel(
            header_frame,
            text="🌀 Anikoto Anime Downloader",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Download anime with subtitles or dubs directly to your computer",
            font=ctk.CTkFont(size=13),
            text_color="gray70"
        )
        subtitle_label.pack(anchor="w")

        # 1. URL & Fetch Card
        url_card = ctk.CTkFrame(self.main_container, corner_radius=10)
        url_card.pack(fill="x", pady=6, padx=2)

        url_inner = ctk.CTkFrame(url_card, fg_color="transparent")
        url_inner.pack(fill="x", padx=14, pady=14)

        ctk.CTkLabel(
            url_inner,
            text="Anime Watch URL",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 4))

        url_input_row = ctk.CTkFrame(url_inner, fg_color="transparent")
        url_input_row.pack(fill="x", pady=(0, 6))

        self.url_entry = ctk.CTkEntry(
            url_input_row,
            placeholder_text="e.g. https://anikoto.cz/watch/one-piece-odmau",
            height=38,
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.fetch_btn = ctk.CTkButton(
            url_input_row,
            text="Fetch Anime",
            width=120,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_fetch_clicked
        )
        self.fetch_btn.pack(side="right")

        self.info_badge = ctk.CTkLabel(
            url_inner,
            text="Paste an anime URL above and click 'Fetch Anime'",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        self.info_badge.pack(anchor="w")

        # 2. Options Card
        options_card = ctk.CTkFrame(self.main_container, corner_radius=10)
        options_card.pack(fill="x", pady=6, padx=2)

        options_inner = ctk.CTkFrame(options_card, fg_color="transparent")
        options_inner.pack(fill="x", padx=14, pady=14)

        ctk.CTkLabel(
            options_inner,
            text="Download Options",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        grid = ctk.CTkFrame(options_inner, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # Left Column: Audio & Quality & Server
        left_col = ctk.CTkFrame(grid, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(left_col, text="Audio Track", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", pady=(0, 2))
        self.audio_seg = ctk.CTkSegmentedButton(
            left_col,
            values=["Sub (Japanese)", "Dub (English)"],
            font=ctk.CTkFont(size=12)
        )
        self.audio_seg.set("Sub (Japanese)")
        self.audio_seg.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(left_col, text="Video Quality", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", pady=(0, 2))
        self.quality_combo = ctk.CTkComboBox(
            left_col,
            values=["1080", "720", "480", "360", "2160"],
            state="readonly"
        )
        self.quality_combo.set("1080")
        self.quality_combo.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(left_col, text="Streaming Server", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", pady=(0, 2))
        self.server_combo = ctk.CTkComboBox(
            left_col,
            values=["Auto (All Sources)", "vidstream-1", "HD-1", "vidstream-2", "kiwi", "vidplay"],
            state="readonly"
        )
        self.server_combo.set("Auto (All Sources)")
        self.server_combo.pack(fill="x", pady=(0, 10))

        # Right Column: Episode Selection & Subtitles
        right_col = ctk.CTkFrame(grid, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(right_col, text="Episodes to Download", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", pady=(0, 2))
        self.ep_mode_var = ctk.StringVar(value="single")

        ep_modes_row = ctk.CTkFrame(right_col, fg_color="transparent")
        ep_modes_row.pack(fill="x", pady=(0, 6))

        ctk.CTkRadioButton(
            ep_modes_row,
            text="Single / Range",
            variable=self.ep_mode_var,
            value="range",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 12))

        ctk.CTkRadioButton(
            ep_modes_row,
            text="All Episodes",
            variable=self.ep_mode_var,
            value="all",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")

        # Range inputs
        range_inputs = ctk.CTkFrame(right_col, fg_color="transparent")
        range_inputs.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(range_inputs, text="From Ep:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 6))
        self.from_ep_entry = ctk.CTkEntry(range_inputs, width=64, height=30)
        self.from_ep_entry.insert(0, "1")
        self.from_ep_entry.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(range_inputs, text="To Ep:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 6))
        self.to_ep_entry = ctk.CTkEntry(range_inputs, width=64, height=30)
        self.to_ep_entry.insert(0, "1")
        self.to_ep_entry.pack(side="left")

        # Subtitles Options
        ctk.CTkLabel(right_col, text="Subtitles", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", pady=(0, 2))
        sub_row = ctk.CTkFrame(right_col, fg_color="transparent")
        sub_row.pack(fill="x")

        self.sub_checkbox = ctk.CTkCheckBox(
            sub_row,
            text="Download .vtt Subtitles",
            font=ctk.CTkFont(size=12)
        )
        self.sub_checkbox.select()
        self.sub_checkbox.pack(side="left", padx=(0, 10))

        self.sub_lang_entry = ctk.CTkEntry(sub_row, width=80, height=30, placeholder_text="English")
        self.sub_lang_entry.insert(0, "English")
        self.sub_lang_entry.pack(side="left")

        # Destination Folder Card
        dest_card = ctk.CTkFrame(self.main_container, corner_radius=10)
        dest_card.pack(fill="x", pady=6, padx=2)

        dest_inner = ctk.CTkFrame(dest_card, fg_color="transparent")
        dest_inner.pack(fill="x", padx=14, pady=12)

        ctk.CTkLabel(
            dest_inner,
            text="Save Folder",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 4))

        dest_row = ctk.CTkFrame(dest_inner, fg_color="transparent")
        dest_row.pack(fill="x")

        self.save_dir_entry = ctk.CTkEntry(dest_row, height=34, font=ctk.CTkFont(size=12))
        self.save_dir_entry.insert(0, get_default_save_dir())
        self.save_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            dest_row,
            text="Browse...",
            width=90,
            height=34,
            command=self._on_browse_folder
        )
        browse_btn.pack(side="right")

        # 3. Actions & Real-Time Progress Card
        act_card = ctk.CTkFrame(self.main_container, corner_radius=10)
        act_card.pack(fill="x", pady=6, padx=2)

        act_inner = ctk.CTkFrame(act_card, fg_color="transparent")
        act_inner.pack(fill="x", padx=14, pady=14)

        # Buttons row
        btn_row = ctk.CTkFrame(act_inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 10))

        self.download_btn = ctk.CTkButton(
            btn_row,
            text="Start Download",
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1f6feb",
            hover_color="#1857ba",
            command=self._on_start_download
        )
        self.download_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=90,
            height=42,
            fg_color="#b62324",
            hover_color="#891a1b",
            state="disabled",
            command=self._on_cancel_download
        )
        self.cancel_btn.pack(side="left", padx=(0, 10))

        self.open_folder_btn = ctk.CTkButton(
            btn_row,
            text="Open Folder",
            width=110,
            height=42,
            fg_color="#238636",
            hover_color="#1a6328",
            command=self._on_open_folder
        )
        self.open_folder_btn.pack(side="right")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(act_inner, height=12)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(0, 8))

        # Status text
        self.status_label = ctk.CTkLabel(
            act_inner,
            text="Ready to download.",
            font=ctk.CTkFont(size=12),
            text_color="gray80"
        )
        self.status_label.pack(anchor="w")

        # 4. Console Log Drawer
        log_card = ctk.CTkFrame(self.main_container, corner_radius=10)
        log_card.pack(fill="both", expand=True, pady=6, padx=2)

        log_inner = ctk.CTkFrame(log_card, fg_color="transparent")
        log_inner.pack(fill="both", expand=True, padx=14, pady=10)

        log_header = ctk.CTkFrame(log_inner, fg_color="transparent")
        log_header.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            log_header,
            text="Console Logs",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")

        clear_btn = ctk.CTkButton(
            log_header,
            text="Clear",
            width=60,
            height=24,
            font=ctk.CTkFont(size=11),
            command=self._clear_logs
        )
        clear_btn.pack(side="right")

        self.log_text = ctk.CTkTextbox(
            log_inner,
            height=120,
            font=ctk.CTkFont(family="Courier", size=11),
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True)

    def _log(self, message):
        self.log_queue.put(message)

    def _start_log_listener(self):
        def check_queue():
            while not self.log_queue.empty():
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert("end", str(msg) + "\n")
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
            self.root.after(100, check_queue)

        self.root.after(100, check_queue)

    def _clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _on_browse_folder(self):
        path = filedialog.askdirectory(initialdir=self.save_dir_entry.get())
        if path:
            self.save_dir_entry.delete(0, "end")
            self.save_dir_entry.insert(0, path)

    def _on_open_folder(self):
        path = self.save_dir_entry.get().strip()
        if not os.path.exists(path):
            messagebox.showwarning("Folder Not Found", f"Directory does not exist:\n{path}")
            return
        system = platform.system()
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _on_fetch_clicked(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste an anime watch URL first.")
            return

        self.fetch_btn.configure(state="disabled", text="Fetching...")
        self.info_badge.configure(text="Fetching anime metadata from server...", text_color="#1f6feb")
        self._log(f"Fetching metadata for: {url}")

        def worker():
            try:
                import requests
                from bs4 import BeautifulSoup
                import re

                session = requests.Session()
                session.headers.update({
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "x-requested-with": "XMLHttpRequest",
                })
                r = session.get(url, timeout=15)
                parsed = urlparse(r.url)
                domain = f"{parsed.scheme}://{parsed.netloc}"

                search = re.search(rf'{domain}/anime/getinfo/(\d+)', r.text)
                if not search:
                    search = re.search(r'/anime/getinfo/(\d+)', r.text)
                if not search:
                    raise Exception("Unable to find anime ID from URL.")

                video_id = search.group(1)
                soup = BeautifulSoup(r.text, 'html.parser')
                title_elem = soup.find('h1', class_='title d-title')
                anime_title = title_elem.get_text(strip=True) if title_elem else "Anime"

                r_ep = session.get(f"{domain}/ajax/episode/list/{video_id}?vrf=", timeout=15)
                ep_soup = BeautifulSoup(r_ep.json().get('result', ''), 'html.parser')
                episodes = ep_soup.find_all('li', {'data-html': 'true'})

                if not episodes:
                    raise Exception("No episodes found for this anime.")

                self.anime_info = {
                    'title': anime_title,
                    'total': len(episodes),
                    'episodes': episodes,
                    'domain': domain,
                    'url': url
                }

                def update_ui():
                    self.fetch_btn.configure(state="normal", text="Fetch Anime")
                    self.info_badge.configure(
                        text=f"Loaded: {anime_title} ({len(episodes)} Episodes)",
                        text_color="#3fb950"
                    )
                    self.from_ep_entry.delete(0, "end")
                    self.from_ep_entry.insert(0, "1")
                    self.to_ep_entry.delete(0, "end")
                    self.to_ep_entry.insert(0, str(len(episodes)))
                    self._log(f"Successfully loaded '{anime_title}' with {len(episodes)} episodes.")

                self.root.after(0, update_ui)

            except Exception as e:
                def on_err():
                    self.fetch_btn.configure(state="normal", text="Fetch Anime")
                    self.info_badge.configure(text=f"Error: {e}", text_color="#f85149")
                    self._log(f"Error fetching anime: {e}")
                    messagebox.showerror("Fetch Failed", f"Could not load anime details:\n{e}")

                self.root.after(0, on_err)

        threading.Thread(target=worker, daemon=True).start()

    def _on_start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter an anime URL.")
            return

        save_path = self.save_dir_entry.get().strip()
        if not save_path:
            messagebox.showwarning("Missing Folder", "Please select a download folder.")
            return

        audio = "sub" if "Sub" in self.audio_seg.get() else "dub"
        quality = self.quality_combo.get()
        source_val = self.server_combo.get()
        if "Auto" in source_val:
            sources_arg = ["megaplay", "vidstream", "kiwi", "vidcloud", "vidplay", "hd"]
        else:
            sources_arg = [source_val.strip().lower()]

        # Episode range
        if self.ep_mode_var.get() == "all":
            range_arg = None
        else:
            from_ep = self.from_ep_entry.get().strip() or "1"
            to_ep = self.to_ep_entry.get().strip() or from_ep
            range_arg = f"{from_ep}-{to_ep}"

        subtitles_enabled = bool(self.sub_checkbox.get())
        sub_lang = self.sub_lang_entry.get().strip() or "English"

        self.is_downloading = True
        self.cancel_requested = False
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.cancel_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.status_label.configure(text="Preparing download...")

        self._log(f"Starting download: audio={audio}, quality={quality}, range={range_arg}, server={source_val}")

        def worker():
            class CLIArgs:
                def __init__(self):
                    self.url = url
                    self.path = save_path
                    self.audio = audio
                    self.quality = quality
                    self.downloader = "yt-dlp"
                    self.source = sources_arg
                    self.subtitles = subtitles_enabled
                    self.subtitle_lang = sub_lang
                    self.range = range_arg
                    self.episode = None
                    self.last = False
                    self.list = False
                    self.debug = False

            args = CLIArgs()

            try:
                self._run_download_pipeline(args)
                status_msg = "All downloads finished successfully!"
            except Exception as e:
                if self.cancel_requested:
                    status_msg = "Download cancelled by user."
                else:
                    status_msg = f"Download ended: {e}"
                self._log(f"Download exception: {e}")

            def on_finish():
                self.is_downloading = False
                self.download_btn.configure(state="normal", text="Start Download")
                self.cancel_btn.configure(state="disabled")
                self.status_label.configure(text=status_msg)
                self._log(status_msg)

            self.root.after(0, on_finish)

        threading.Thread(target=worker, daemon=True).start()

    def _on_cancel_download(self):
        self.cancel_requested = True
        self.cancel_btn.configure(state="disabled", text="Cancelling...")
        self.status_label.configure(text="Cancelling download...")
        self._log("Cancel requested...")

    def _run_download_pipeline(self, args):
        import requests
        from bs4 import BeautifulSoup
        import re
        from anikoto.anikoto import (
            subtitles as download_subs,
            download as run_download,
            player_parameters,
            decrypt_source,
            signed_url
        )

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "x-requested-with": "XMLHttpRequest",
        })

        self._log(f"Contacting anime portal: {args.url}")
        r = session.get(args.url)
        parsed = urlparse(r.url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        search = re.search(rf'{domain}/anime/getinfo/(\d+)', r.text)
        if not search:
            search = re.search(r'/anime/getinfo/(\d+)', r.text)
        if not search:
            raise Exception("Unable to find anime ID.")

        video_id = search.group(1)
        soup = BeautifulSoup(r.text, 'html.parser')
        title_elem = soup.find('h1', class_='title d-title')
        anime_title = title_elem.get_text(strip=True) if title_elem else "Anime"

        r_ep = session.get(f"{domain}/ajax/episode/list/{video_id}?vrf=")
        episodes = BeautifulSoup(r_ep.json().get('result', ''), 'html.parser').find_all('li', {'data-html': 'true'})

        episode_data = []
        for i, ep in enumerate(episodes, 1):
            t = ep.get('title')
            a = ep.find('a')
            data_ids = a.get('data-ids') if a else None
            data_mal = a.get('data-mal') if a else None
            data_ts = a.get('data-timestamp') if a else None
            episode_data.append({
                'title': t,
                'data-ids': data_ids,
                'data-mel': data_mal,
                'data-timestamp': data_ts,
                'number': i
            })

        # Apply range
        if args.range:
            start, end = map(int, args.range.split('-'))
            target_episodes = episode_data[start - 1:end]
        else:
            target_episodes = episode_data

        total_eps = len(target_episodes)
        self._log(f"Processing {total_eps} episode(s)...")

        for ep_idx, ep in enumerate(target_episodes, 1):
            if self.cancel_requested:
                break

            num = ep['number']
            ep_title = ep['title']
            msg = f"[{ep_idx}/{total_eps}] E{num}: {ep_title}"
            self.root.after(0, lambda m=msg: self.status_label.configure(text=m))
            self._log(msg)

            # Get servers
            url_srv = f"{domain}/ajax/server/list"
            r_srv = session.get(url_srv, params={"servers": ep['data-ids']})
            soup_srv = BeautifulSoup(r_srv.json().get('result', ''), 'html.parser')

            server_data = []
            for sdiv in soup_srv.find_all('div', class_='type'):
                stype = sdiv.get('data-type', '').upper()
                for li in sdiv.find_all('li'):
                    server_data.append({
                        'type': stype,
                        'data-link-id': li.get('data-link-id'),
                        'li': li.text.strip()
                    })

            downloaded = False
            for srv in server_data:
                if self.cancel_requested:
                    break

                if srv['type'].lower() != args.audio.lower():
                    continue

                full_source = srv['li'].lower().strip()
                base_source = full_source.split('-')[0].strip() if '-' in full_source else full_source
                user_sources = [s.lower().strip() for s in args.source]
                if full_source not in user_sources and base_source not in user_sources:
                    continue

                # Fetch stream URL for server
                try:
                    r_link = session.get(f"{domain}/ajax/server", params={"get": srv['data-link-id']})
                    embed_url = r_link.json().get('result', {}).get('url')
                    if not embed_url:
                        continue

                    main_r = session.get(embed_url, headers={"referer": f"{domain}/"})
                    soup_embed = BeautifulSoup(main_r.text, "html.parser")
                    script = next((s["src"] for s in soup_embed.select("script[src]") if "e1-player" in s["src"]), None)
                    if not script:
                        continue

                    js = session.get(script).text
                    key, iv, secret, ttl = player_parameters(js)

                    data_id_match = re.search(r' data-id=\"(\d+)\"', main_r.text)
                    if not data_id_match:
                        continue
                    data_id = data_id_match.group(1)

                    if '/videojs/' in embed_url:
                        sources_endpoint = "https://megaplay.buzz/videojs/stream/getSourcesNew"
                    else:
                        sources_endpoint = "https://megaplay.buzz/stream/getSourcesNew"

                    r_sources = session.get(
                        sources_endpoint,
                        params={"id": data_id, "id": data_id},
                        headers={"referer": embed_url, "x-requested-with": "XMLHttpRequest"}
                    )

                    sources_json = r_sources.json()
                    if 'enc' not in sources_json:
                        continue

                    m3u8_url = decrypt_source(sources_json["enc"], key, iv)
                    if isinstance(m3u8_url, list):
                        m3u8_url = next((s["file"] for s in m3u8_url if isinstance(s, dict) and s.get("file")), None)
                    elif isinstance(m3u8_url, dict):
                        m3u8_url = m3u8_url.get("file")

                    m3u8_url = signed_url(m3u8_url, secret, ttl)

                    # Subtitles
                    if args.subtitles:
                        try:
                            download_subs(sources_json, session, args, anime_title, num, ep_title)
                        except Exception as sub_err:
                            self._log(f"Subtitle warning: {sub_err}")

                    # Download with progress
                    def progress_hook(d):
                        if self.cancel_requested:
                            raise Exception("Download cancelled by user.")
                        if d.get('status') == 'downloading':
                            total = d.get('total_bytes') or d.get('total_bytes_estimate')
                            downloaded_b = d.get('downloaded_bytes', 0)
                            if total:
                                pct = downloaded_b / total
                                self.root.after(0, lambda p=pct: self.progress_bar.set(p))
                            speed = d.get('_speed_str', '')
                            eta = d.get('_eta_str', '')
                            status_txt = f"E{num} - {speed} (ETA: {eta})"
                            self.root.after(0, lambda s=status_txt: self.status_label.configure(text=s))

                    # Inject progress hook into yt-dlp options
                    args.downloader = 'yt-dlp'
                    self._log(f"Downloading E{num} from server '{srv['li']}'...")
                    run_download(m3u8_url, "https://megaplay.buzz/", args.path, anime_title, ep_title, num, args)
                    downloaded = True
                    break

                except Exception as srv_err:
                    self._log(f"Server {srv['li']} error: {srv_err}")
                    continue

            if not downloaded and not self.cancel_requested:
                self._log(f"Warning: Could not download E{num} from selected servers.")

    def run(self):
        self.root.mainloop()


def run_gui():
    app = AnikotoGUI()
    app.run()


if __name__ == "__main__":
    run_gui()
