import json
import logging
import re
from ..common import Episode, Metadata, Season, open_url

# language: zh
# Ex:"https://tv.sohu.com/v/MjAyMjA4MTEvbjYwMTIwNDk3MS5zaHRtbA==.html?txid=9075b2a7de230eeef8505336cfdc34ae"
def sohu_extractor(url):
    logging.info("sohu_extractor is called")
    webPage = open_url(url)
    playlistId = re.search(r'playlistId=\"(.*?)\"', str(webPage)).group(1)
    logging.info(f"playlistId: {playlistId}")
    apiRequest = f"https://pl.hd.sohu.com/videolist?playlistid={playlistId}&pagesize=999&order=0&callback="
    logging.debug(f"API request: {apiRequest}")
    soureData = json.loads(open_url(apiRequest, "gb18030"))
    album_url = soureData["albumPageUrl"]
    logging.info(f"album_url: {album_url}")
    name = soureData["albumName"]
    logging.info(f"name: {name}")
    description = soureData["albumDesc"]
    logging.info(f"description: {description}")
    
    # Extract poster if available
    poster = None
    if "data" in soureData and "imageUrl" in soureData["data"]:
        poster = soureData["data"]["imageUrl"]
        logging.info(f"poster: {poster}")

    episodes = {}
    for episode in soureData["videos"]:
        episode_number = episode["order"]
        episode_name = episode["subName"]
        episode_air_date = episode["publishTime"]
        episode_runtime = round(float(episode["playLength"])/60)
        episode_overview = episode["videoDesc"]
        episode_backdrop = episode["tvPicExt"]

        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    return Metadata(
        url=url, 
        language="zh-CN", 
        title=name, 
        overview=description,
        poster=poster,
        seasons=[Season(None, episodes=episodes)]
    )