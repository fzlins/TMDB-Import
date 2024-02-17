import json
from urllib.parse import urlparse
import logging
from datetime import datetime
from ..common import Episode, open_url

# ex: https://www.bilibili.com/bangumi/media/md28234541
def bilibili_extractor(url):
    logging.info("bilibili_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    mediaID = ''.join(filter(str.isdigit, urlPath))
    apiRequest = f"https://api.bilibili.com/pgc/review/user?media_id={mediaID}"
    logging.debug(f"API request url: {apiRequest}")
    mediaData = json.loads(open_url(apiRequest))

    season_name = mediaData["result"]["media"]["title"]
    logging.info(f"name: {season_name}")
    season_poster = mediaData["result"]["media"]["cover"]
    logging.info(f"poster: {season_poster}")
    season_backdrop = mediaData["result"]["media"]["horizontal_picture"]
    logging.info(f"backdrop: {season_backdrop}")
    
    seasonID = mediaData["result"]["media"]["season_id"]
    apiRequest = f"https://api.bilibili.com/pgc/view/web/season?season_id={seasonID}"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    episodes = {}
    episode_number = 1
    for episode in soureData["result"]["episodes"]:
        if episode["badge"] == "预告":
            continue

        if episode["title"].__contains__("（上）") or episode["title"].__contains__("（下）"):
            episode_name = episode["title"] + " " + episode["long_title"]
        else:
            episode_name = episode["long_title"]
        episode_air_date = datetime.fromtimestamp(episode["pub_time"]).date()
        episode_runtime = round(episode["duration"]/60000)
        episode_overview = ""
        episode_backdrop = episode["cover"]
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episode_number = episode_number + 1

    return episodes