import json
import re
import urllib.request
import urllib.parse
import logging
from datetime import date, datetime, timezone, timedelta
from ..common import Episode, Metadata, Season

_PLATFORM_URL = "https://platform-api.tver.jp"
_SERVICE_URL = "https://service-api.tver.jp"
_STATICS_URL = "https://statics.tver.jp"

_HEADERS = {
    "x-tver-platform-type": "web",
    "Origin": "https://tver.jp",
    "Referer": "https://tver.jp/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

_JST = timezone(timedelta(hours=9))

# Keywords identifying non-main seasons to skip
_SKIP_SEASON_KEYWORDS = ["解説", "ダイジェスト", "予告", "digest", "preview"]


def _request(url, extra_headers=None, data=None):
    req = urllib.request.Request(url, data=data)
    for k, v in _HEADERS.items():
        req.add_header(k, v)
    if extra_headers:
        for k, v in extra_headers.items():
            req.add_header(k, v)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def _parse_ep_number(title):
    """Return the integer episode number from a Japanese title like '第5話 ...' or None."""
    m = re.search(r"第(\d+)話", title)
    return int(m.group(1)) if m else None


def _parse_broadcast_date(label):
    """Parse a broadcastDateLabel like '5月7日(木)放送分' into a YYYY-MM-DD string."""
    m = re.search(r"(\d+)月(\d+)日", label)
    if not m:
        return ""
    month, day = int(m.group(1)), int(m.group(2))
    today = date.today()
    candidate = date(today.year, month, day)
    # If the candidate date is more than ~6 months in the future it's last year
    if (candidate - today).days > 180:
        candidate = date(today.year - 1, month, day)
    return candidate.strftime("%Y-%m-%d")


# ex: https://tver.jp/series/srx7pm6gbl
def tver_extractor(url):
    logging.info("tver_extractor is called")

    url_data = urllib.parse.urlparse(url)
    series_id = url_data.path.strip("/").split("/")[-1]
    logging.debug(f"Series ID: {series_id}")

    # Step 1: Create anonymous platform session
    session_data = _request(
        f"{_PLATFORM_URL}/v2/api/platform_users/browser/create",
        extra_headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=b"device_type=pc",
    )
    platform_uid = session_data["result"]["platform_uid"]
    platform_token = session_data["result"]["platform_token"]
    logging.debug(f"Platform session created (uid prefix: {platform_uid[:8]})")

    # Step 2: Get series metadata (title, poster, etc.)
    series_data = _request(
        f"{_SERVICE_URL}/api/v1/callSeries/{series_id}"
    )
    series_info = series_data.get("result", {})
    series_title = series_info.get("title", "")
    series_poster = ""
    if "thumbnailPath" in series_info:
        series_poster = f"{_STATICS_URL}{series_info['thumbnailPath']}"
    
    logging.info(f"Series title: {series_title}")
    if series_poster:
        logging.info(f"Series poster: {series_poster}")

    # Step 3: Get all seasons for the series
    seasons_data = _request(
        f"{_SERVICE_URL}/api/v1/callSeriesSeasons/{series_id}"
    )

    # Step 4: Collect episodes from main seasons only
    episode_list = []
    seen_ids = set()

    for item in seasons_data.get("result", {}).get("contents", []):
        if item.get("type") != "season":
            continue
        season = item.get("content", {})
        season_title = season.get("title", "")

        if any(kw in season_title for kw in _SKIP_SEASON_KEYWORDS):
            logging.debug(f"Skipping season: {season_title}")
            continue

        season_id = season.get("id")
        logging.debug(f"Processing season: {season_title} ({season_id})")

        ep_data = _request(
            f"{_PLATFORM_URL}/service/api/v1/callSeasonEpisodes/{season_id}"
            f"?platform_uid={platform_uid}&platform_token={platform_token}"
        )

        for ep_item in ep_data.get("result", {}).get("contents", []):
            if ep_item.get("type") != "episode":
                continue
            ep = ep_item.get("content", {})
            ep_id = ep.get("id")
            if ep_id not in seen_ids:
                seen_ids.add(ep_id)
                episode_list.append(ep)

    # Sort by parsed episode number; episodes without a number go to the end
    episode_list.sort(
        key=lambda e: (_parse_ep_number(e.get("title", "")) is None,
                       _parse_ep_number(e.get("title", "")) or 0)
    )

    # Step 5: Fetch episode details and build Episode objects
    episodes = {}
    fallback_number = 1

    for ep in episode_list:
        ep_id = ep.get("id")
        ep_version = str(ep.get("version", ""))
        title = ep.get("title", "")
        duration_sec = ep.get("duration", 0)
        runtime = round(duration_sec / 60) if duration_sec else ""
        thumbnail_path = ep.get("thumbnailPath", "")
        backdrop = f"{_STATICS_URL}{thumbnail_path}" if thumbnail_path else ""

        ep_number = _parse_ep_number(title)
        # Strip the episode-number prefix (e.g. "第5話 ") from the name
        ep_name = re.sub(r"^第\d+話\s*", "", title) or title

        description = ""
        air_date = ""
        try:
            statics_data = _request(
                f"{_STATICS_URL}/content/episode/{ep_id}.json?v={ep_version}"
            )
            description = statics_data.get("description", "")
            start_at = statics_data.get("viewStatus", {}).get("startAt")
            if start_at:
                air_date = datetime.fromtimestamp(start_at, tz=_JST).strftime("%Y-%m-%d")
        except Exception as e:
            logging.warning(f"Could not fetch statics for episode {ep_id}: {e}")
            # Fall back to parsing the broadcast date label
            broadcast_label = ep.get("broadcastDateLabel", "")
            if broadcast_label:
                air_date = _parse_broadcast_date(broadcast_label)

        if ep_number is None:
            ep_number = fallback_number

        # Advance fallback counter past any explicitly numbered episodes
        fallback_number = max(fallback_number, ep_number) + 1

        episodes[ep_number] = Episode(
            ep_number, ep_name, air_date, runtime, description, backdrop
        )

    return Metadata(
        url=url, 
        id=series_id, 
        title=series_title,
        poster=series_poster,
        language="ja-JP", 
        seasons=[Season(None, episodes=episodes)]
    )
