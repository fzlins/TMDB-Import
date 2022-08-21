import json
import urllib.request
from urllib.parse import urlparse
import logging
from ..common import Episode

# language: zh
# backdrop: 860*484
# Ex:"https://w.mgtv.com/b/419629/17004788.html"
def mgtv_extractor(url):
    logging.info("mgtv_extractor is called")

    videoID =  url.rsplit('/', 1)[-1].split('.html')[0]
    apiRequest = f"https://pcweb.api.mgtv.com/episode/list?_support=10000000&version=5.5.35&video_id={videoID}&page=0&size=50&&callback="
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode('utf-8-sig'))
    episodes = {}
    for episode in soureData["data"]["list"]:
        if episode["isIntact"] == "1":
            episode_number = episode["t1"]
            episode_name = episode["t2"]
            episode_air_date = episode["ts"].split(' ')[0]
            episode_runtime = episode["time"].split(':')[0]
            episode_overview = ""
            episode_backdrop = episode["img"].rsplit('_', 1)[0]
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
    return episodes