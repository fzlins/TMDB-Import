import json
import re
from urllib.parse import urlparse
import logging
from ..common import Episode, Metadata, Season, open_url

# ex: https://www.bilibili.tv/en/media/2070355
def bilibili_tv_extractor(url):
    logging.info("bilibili_tv_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    seasonID = urlPath.split('/')[-1]
    apiRequest = f"https://api.bilibili.tv/intl/gateway/web/v2/ogv/play/season_info?season_id={seasonID}&platform=web"
    logging.debug(f"API request url: {apiRequest}")
    seasonData = json.loads(open_url(apiRequest))

    season = seasonData["data"]["season"]
    season_name = season["title"]
    logging.info(f"name: {season_name}")
    season_poster = season.get("vertical_cover", "")
    logging.info(f"poster: {season_poster}")
    season_backdrop = season.get("horizontal_cover", "")
    logging.info(f"backdrop: {season_backdrop}")

    apiRequest = f"https://api.bilibili.tv/intl/gateway/web/v2/ogv/play/episodes?season_id={seasonID}&platform=web"
    logging.debug(f"API request url: {apiRequest}")
    episodesData = json.loads(open_url(apiRequest))

    episodes = {}
    episode_number = 1
    for section in episodesData["data"]["sections"]:
        for episode in section["episodes"]:
            long_title = episode.get("long_title_display", "")
            short_title = episode.get("short_title_display", "")
            episode_name = long_title if long_title else short_title
            # Leave name empty if it's just a plain episode number like E1, E2, ...
            if re.fullmatch(r'E\d+', episode_name):
                episode_name = ""
            publish_time = episode.get("publish_time", "")
            episode_air_date = publish_time[:10] if publish_time else "null"
            episode_backdrop = episode.get("cover", "")
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, "", "", episode_backdrop)
            episode_number += 1

    return Metadata(url=url, name=season_name, poster=season_poster, backdrop=season_backdrop, seasons=[Season(None, episodes=episodes)])
