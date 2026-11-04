"""
Anikoto - Fast anime downloader with GUI and CLI support.
"""

import os
import sys

# Ensure package directory is in sys.path if needed
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from anikoto.anikoto import (
    clean_name,
    configure_logging,
    player_parameters,
    decrypt_source,
    signed_url,
    subtitles,
    download,
    main,
)

__all__ = [
    "clean_name",
    "configure_logging",
    "player_parameters",
    "decrypt_source",
    "signed_url",
    "subtitles",
    "download",
    "main",
]
