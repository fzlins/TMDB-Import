import json
import logging
import urllib.request
from datetime import datetime
from urllib.parse import urlencode, urlparse

from ..common import Episode, Metadata, Season

API_ENDPOINT = "https://prod-fms.kocowa.com/api/v01/fe/content/get"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

LANGUAGE_MAP = {
    "ko_kr": "ko-KR",
    "en_us": "en-US",
    "es": "es-ES",
    "es_us": "es-US",
    "pt": "pt-PT",
    "pt_br": "pt-BR",
    "zh_cn": "zh-CN",
}

TITLE_KEY_MAP = {
    "ko_kr": "ko",
    "en_us": "en",
    "es": "es",
    "es_us": "es",
    "pt": "pt",
    "pt_br": "pt",
    "zh_cn": "zh-Hans",
}


def _extract_kocowa_id(url):
    path_parts = [part for part in urlparse(url).path.split("/") if part]
    if "season" in path_parts:
        idx = path_parts.index("season")
        if idx + 1 < len(path_parts) and path_parts[idx + 1].isdigit():
            return path_parts[idx + 1]

    for part in path_parts:
        if part.isdigit():
            return part
    return None


def _extract_url_lang(url):
    path_parts = [part for part in urlparse(url).path.split("/") if part]
    for part in path_parts:
        if "_" in part:
            lowered = part.lower()
            if lowered in LANGUAGE_MAP:
                return lowered
    return "en_us"


def _pick_lang_text(text_map, lang_key):
    if not isinstance(text_map, dict):
        return ""

    value = text_map.get(lang_key)
    if value:
        return value
    return ""


def _kocowa_request(content_id, offset=0, limit=100, order="asc"):
    query = urlencode(
        {
            "id": content_id,
            "offset": offset,
            "limit": limit,
            "order": order,
        }
    )
    request = urllib.request.Request(
        f"{API_ENDPOINT}?{query}",
        headers={
            "Authorization": "anonymous",
            "Origin": "https://www.kocowa.com",
            "Referer": "https://www.kocowa.com/",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": USER_AGENT,
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def kocowa_extractor(url):
    logging.info("kocowa_extractor is called")

    content_id = _extract_kocowa_id(url)
    if not content_id:
        logging.error("Failed to extract Kocowa content ID from URL")
        return Metadata(url=url, seasons=[])

    url_lang = _extract_url_lang(url)
    metadata_language = LANGUAGE_MAP.get(url_lang, "en-US")
    title_lang_key = TITLE_KEY_MAP.get(url_lang, "en")

    try:
        source_data = _kocowa_request(content_id=content_id, offset=0, limit=100, order="asc")
    except Exception as e:
        logging.error(f"Failed to request Kocowa API: {e}")
        return Metadata(url=url, id=content_id, seasons=[])

    content = source_data.get("object", {})
    meta = content.get("meta", {})

    title = _pick_lang_text(meta.get("title", {}), title_lang_key)
    overview = _pick_lang_text(meta.get("description", {}), title_lang_key)
    if not overview:
        overview = _pick_lang_text(meta.get("summary", {}), title_lang_key)

    poster = meta.get("poster", {}).get("portrait") or ""
    backdrop = meta.get("poster", {}).get("landscape") or ""

    release_date = ""
    start_date = content.get("start_date")
    if start_date:
        release_date = start_date.split("T")[0]

    episodes = {}
    page_size = 100
    offset = 0
    total_count = 0

    while True:
        if offset == 0:
            page_data = source_data
        else:
            try:
                page_data = _kocowa_request(content_id=content_id, offset=offset, limit=page_size, order="asc")
            except Exception as e:
                logging.error(f"Failed to request Kocowa episode page (offset={offset}): {e}")
                break

        page_root = page_data.get("object", {})
        next_episodes = page_root.get("next_episodes", {})
        total_count = int(next_episodes.get("total_count") or total_count or 0)
        objects = next_episodes.get("objects", [])

        if not objects:
            break

        for episode in objects:
            episode_meta = episode.get("meta", {})
            episode_number = episode_meta.get("episode_number")
            if episode_number is None:
                continue

            episode_name = _pick_lang_text(episode_meta.get("title", {}), title_lang_key)
            episode_overview = _pick_lang_text(episode_meta.get("description", {}), title_lang_key)
            if not episode_overview:
                episode_overview = _pick_lang_text(episode_meta.get("summary", {}), title_lang_key)

            episode_air_date = ""
            air_ts = episode_meta.get("onair_date")
            if air_ts:
                try:
                    episode_air_date = datetime.utcfromtimestamp(int(air_ts) / 1000).date()
                except (ValueError, OSError, TypeError):
                    episode_air_date = ""

            episode_runtime = ""
            duration_sec = episode_meta.get("duration")
            if duration_sec:
                try:
                    episode_runtime = round(int(duration_sec) / 60)
                except (ValueError, TypeError):
                    episode_runtime = ""

            episode_backdrop = episode_meta.get("poster", {}).get("landscape") or ""

            episodes[episode_number] = Episode(
                episode_number,
                episode_name,
                episode_air_date,
                episode_runtime,
                episode_overview,
                episode_backdrop,
            )

        offset += len(objects)
        if total_count and offset >= total_count:
            break
        if len(objects) < page_size:
            break

    season_number = meta.get("season_number")
    season_name = _pick_lang_text(meta.get("parent_title", {}), title_lang_key) or title

    logging.info(f"Successfully extracted {len(episodes)} episodes")
    return Metadata(
        url=url,
        id=content_id,
        title=title,
        overview=overview,
        poster=poster,
        backdrop=backdrop,
        language=metadata_language,
        release_date=release_date,
        seasons=[
            Season(
                season_number=season_number,
                name=season_name,
                overview=overview,
                poster=poster,
                episodes=episodes,
            )
        ],
    )