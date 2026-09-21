import json
import logging
import re
from datetime import datetime

from ..common import Episode, Metadata, Season, open_url

API_KEY = "1e7952d0917d6aab1f0293a063697610"
STATIC_PARAMS = "screenCode=CSSD0100&networkCode=CSND0900&osCode=CSOD0900&teleCode=CSCD0900&apiKey=" + API_KEY
IMAGE_BASE_URL = "https://image.tving.com"


def _localized(text_map, lang="ko"):
    if isinstance(text_map, dict):
        return text_map.get(lang, "") or ""
    return text_map or ""


def _image_url(image_list):
    if not image_list:
        return ""
    url = image_list[0].get("url", "")
    return f"{IMAGE_BASE_URL}{url}" if url else ""


# language: ko
# ex: "https://www.tving.com/contents/P001665114" (program landing page)
# ex: "https://www.tving.com/contents/E003846992" (single episode page)
def tving_extractor(url):
    logging.info("tving_extractor is called")

    code_match = re.search(r'/contents/([A-Za-z0-9]+)', url)
    if not code_match:
        raise ValueError("Could not extract content code from the URL")
    content_code = code_match.group(1)

    # content/info resolves either a program code or an episode code to the
    # series' program_code, and returns show-level title/synopsis/poster.
    info_request = f"https://api.tving.com/v2/media/content/info?mediaCode={content_code}&{STATIC_PARAMS}"
    logging.debug(f"API request url: {info_request}")
    info_data = json.loads(open_url(info_request))
    content = info_data.get("body", {}).get("content", {})
    if not content:
        raise ValueError(f"Could not fetch content info for TVING content {content_code}")

    program_code = content.get("program_code", content_code)
    show_title = content.get("title", "")
    show_overview = content.get("synopsis", "")
    show_images = content.get("image") or []
    show_poster = _image_url(show_images)
    show_backdrop = _image_url(list(reversed(show_images)))

    episodes = {}
    page_no = 1
    page_size = 50
    while True:
        episodes_request = (
            f"https://api.tving.com/v2/media/frequency/program/{program_code}"
            f"?order=new&cacheType=main&pageNo={page_no}&pageSize={page_size}"
            f"&adult=all&free=all&guest=all&scope=all&{STATIC_PARAMS}"
        )
        logging.debug(f"API request url: {episodes_request}")
        episodes_data = json.loads(open_url(episodes_request))
        body = episodes_data.get("body", {})
        result = body.get("result", [])

        for item in result:
            episode = item.get("episode", {})

            episode_number = episode.get("frequency")
            if episode_number is None:
                episode_number = len(episodes) + 1
            else:
                episode_number = int(episode_number)

            name = _localized(item.get("vod_name")) or _localized(episode.get("name"))
            name = re.sub(r'^\d+\.\s*', '', name).strip()

            air_date = "null"
            broadcast_date = episode.get("broadcast_date")
            if broadcast_date:
                air_date = datetime.strptime(str(broadcast_date), "%Y%m%d").strftime("%Y-%m-%d")

            duration = episode.get("duration")
            runtime = round(int(duration) / 60) if duration else ""

            overview = _localized(episode.get("synopsis"))
            backdrop = _image_url(episode.get("image"))

            episodes[episode_number] = Episode(episode_number, name, air_date, runtime, overview, backdrop)

        if body.get("has_more") != "Y":
            break
        page_no += 1

    if not episodes:
        raise ValueError(f"No episodes found for TVING content {content_code}")

    return Metadata(
        url=url,
        id=program_code,
        title=show_title,
        language="ko-KR",
        overview=show_overview,
        poster=show_poster,
        backdrop=show_backdrop,
        seasons=[Season(None, episodes=episodes)],
    )

