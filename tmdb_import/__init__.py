"""
TMDB-Import: Extract metadata from streaming platforms
"""

from .extractor import extract_from_url
from .common import Metadata, Season, Episode, save_metadata_json, create_csv

__version__ = "1.0.0"
__all__ = [
    "extract_from_url",
    "Metadata",
    "Season", 
    "Episode",
    "save_metadata_json",
    "create_csv",
]
