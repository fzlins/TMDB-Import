"""
Chinese variant conversion using OpenCC.

Converts text fields in Metadata objects between Chinese variants
(Simplified / Traditional) based on the `chinese_convert` config option.

Supported targets:
  zh-CN  ->  t2s   (any Traditional -> Simplified)
  zh-TW  ->  s2twp (Simplified -> Taiwan Traditional, with phrase conversion)
  zh-HK  ->  s2hk  (Simplified -> Hong Kong Traditional)

Conversion is only triggered when metadata.language starts with "zh"
(covers zh-CN, zh-TW, zh-HK, zh-SG, etc.).
"""

import logging
from ..common import Metadata, Season, Episode, Person, config

# OpenCC config string for each supported target variant
_OPENCC_CONFIGS = {
    "zh-CN": "t2s",
    "zh-TW": "s2twp",
    "zh-HK": "s2hk",
}

# Punctuation translation tables: OpenCC only converts characters, not punctuation.
# These tables handle quotation mark style differences between variants.
#   Simplified Chinese uses curly quotes: “” ‘’
#   Traditional Chinese uses corner brackets: 「」 『』
_PUNCT_TABLES = {
    "zh-CN": str.maketrans("「」『』", "“”‘’"),
    "zh-TW": str.maketrans("“”‘’", "「」『』"),
    "zh-HK": str.maketrans("“”‘’", "「」『』"),
}

# Lazy singleton converter instance (initialized once on first convert call)
_converter = None


def _get_converter(target: str):
    """Return a cached OpenCC converter for *target*, creating it if needed."""
    global _converter
    if _converter is not None:
        return _converter


    try:
        import opencc
    except ImportError:
        raise ImportError(
            "opencc-python-reimplemented is required for Chinese conversion. "
            "Run: pip install opencc-python-reimplemented"
        )

    opencc_config = _OPENCC_CONFIGS.get(target)
    if opencc_config is None:
        raise ValueError(
            f"Unsupported chinese_convert target '{target}'. "
            f"Valid values: {', '.join(_OPENCC_CONFIGS)}"
        )

    _converter = opencc.OpenCC(opencc_config)
    logging.info(f"OpenCC converter initialised: {target} ({opencc_config})")
    return _converter


def is_chinese_language(language: str) -> bool:
    """Return True if *language* is a Chinese locale (any zh-* variant)."""
    return bool(language and language.lower().startswith("zh"))


def _convert_text(text: str, converter, punct_table=None) -> str:
    """Convert *text* with *converter*, returning the original on None/empty."""
    if not text:
        return text
    result = converter.convert(text)
    if punct_table:
        result = result.translate(punct_table)
    return result


def convert_metadata(metadata: Metadata, target: str) -> None:
    """
    Convert all text fields in *metadata* in-place to the *target* Chinese variant.

    Fields converted:
      - Metadata.name, Metadata.overview
      - Season.name, Season.overview  (for every season)
      - Episode.name, Episode.overview (for every episode in every season)
      - Person.name, Person.overview   (crew and guest_stars in every season)
    """
    converter = _get_converter(target)
    punct_table = _PUNCT_TABLES.get(target)

    # Top-level fields
    metadata.name = _convert_text(metadata.name, converter, punct_table)
    metadata.overview = _convert_text(metadata.overview, converter, punct_table)

    if not metadata.seasons:
        return

    for season in metadata.seasons:
        if not isinstance(season, Season):
            continue

        season.name = _convert_text(season.name, converter, punct_table)
        season.overview = _convert_text(season.overview, converter, punct_table)

        # Episodes
        episodes = season.episodes
        if isinstance(episodes, dict):
            for episode in episodes.values():
                if isinstance(episode, Episode):
                    episode.name = _convert_text(episode.name, converter, punct_table)
                    episode.overview = _convert_text(episode.overview, converter, punct_table)
        elif isinstance(episodes, list):
            for episode in episodes:
                if isinstance(episode, Episode):
                    episode.name = _convert_text(episode.name, converter, punct_table)
                    episode.overview = _convert_text(episode.overview, converter, punct_table)

        # Crew / guest stars
        for person_list in (season.crew, season.guest_stars):
            if not person_list:
                continue
            for person in person_list:
                if isinstance(person, Person):
                    person.name = _convert_text(person.name, converter, punct_table)
                    person.overview = _convert_text(person.overview, converter, punct_table)
