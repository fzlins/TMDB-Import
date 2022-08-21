import json
import urllib.request
from urllib.parse import urlparse
import logging
from datetime import datetime
from ..common import Episode

# ex: https://www.bilibili.com/bangumi/media/md28234541
def bilibili_extractor(url):
    logging.info("bilibili_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    mediaID = ''.join(filter(str.isdigit, urlPath))
    apiRequest = f"https://api.bilibili.com/pgc/review/user?media_id={mediaID}"
    logging.info(f"API request url: {apiRequest}")
    mediaData = json.loads(urllib.request.urlopen(apiRequest).read().decode('utf-8-sig'))
    
    seasonID = mediaData["result"]["media"]["season_id"]
    apiRequest = f"https://api.bilibili.com/pgc/view/web/season?season_id={seasonID}"
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode('utf-8-sig'))
    episodes = {}
    for episode in soureData["result"]["episodes"]:
        episode_number = episode["title"]
        episode_name = episode["long_title"]
        episode_air_date = datetime.fromtimestamp(episode["pub_time"]).date()
        episode_runtime = round(episode["duration"]/60000)
        episode_overview = ""
        episode_backdrop = episode["cover"]
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    return episodes