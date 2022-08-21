import json
import urllib.request
import logging
import re
from datetime import datetime
from ..common import Episode

# language: zh
# Ex:"https://www.iqiyi.com/v_ik3832z0go.html"
def iqiyi_extractor(url):
    logging.info("iqiyi_extractor is detected")
    webPage = urllib.request.urlopen(url).read()
    albumId = re.search(r'\"albumId\":(.*?),', str(webPage)).group(1)
    apiRequest = f"https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={albumId}&page=1&size=999&callback="
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode('utf-8-sig'))
    episodes = {}
    for episode in soureData["data"]["epsodelist"]:
        episode_number = episode["order"]
        episode_name = episode["subtitle"]
        episode_air_date = datetime.fromtimestamp(episode["publishTime"]/1000).date()
        episode_runtime = episode["duration"].split(':')[0]
        episode_overview = episode["description"]
        episode_backdrop = episode["imageUrl"]
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    return episodes