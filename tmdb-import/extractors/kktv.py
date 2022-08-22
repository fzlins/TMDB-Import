import json
import urllib.request
from urllib.parse import urlparse
import logging
from datetime import datetime
from ..common import Episode

# ex: https://www.kktv.me/titles/01000577
def kktv_extractor(url):
    logging.info("kktv_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    title = urlPath.rsplit('/', 1)[-1]
    apiRequest = f"https://api.kktv.me//api.kktv.me/v3/titles/{title}"
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
    episodes = {}
    episodeNumber = 1
    for episode in soureData["data"]["series"][0]["episodes"]:
        episode_number = episodeNumber
        episode_name = episode["title"]
        episode_air_date = datetime.fromtimestamp(episode["publish_time"]).date()
        episode_runtime = round(int(episode["duration"])/60)
        episode_overview = ""
        episode_backdrop = episode["still"].replace(".xs.",".md.")
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episodeNumber = episodeNumber + 1

    return episodes