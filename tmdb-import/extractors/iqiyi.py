import json
import logging
import re
from datetime import datetime
from ..common import Episode, open_url

# language: zh
# Ex:"https://www.iqiyi.com/v_ik3832z0go.html"
def iqiyi_extractor(url):
    logging.info("iqiyi_extractor is called")
    webPage = open_url(url)
    if url.__contains__("iqiyi.com/lib/m_"):
        albumId = re.search(r'movlibalbumaid=\"(\d+)\"', str(webPage)).group(1)
    elif re.search(r'iqiyi\.com/a_', url):
        albumId = re.search(r'data-album-id="(\d+)"', str(webPage)).group(1)
    else:
        albumId = re.search(r'\"albumId\":(\d+),\"channelId', str(webPage)).group(1)
    logging.info(f"album_id: {albumId}")
    apiRequest = f"https://pcw-api.iqiyi.com/album/album/baseinfo/{albumId}"
    logging.debug(f"API request: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    album_url = soureData["data"]["url"]
    logging.info(f"album_url: {album_url}")
    name = soureData["data"]["name"]
    logging.info(f"name: {name}")
    cover = soureData["data"]["imageUrl"]
    logging.info(f"Image: {cover}")
    description = soureData["data"]["description"]
    logging.info(f"description: {description}")

    apiRequest = f"https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={albumId}&page=1&size=999&callback="
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    episodes = {}
    for episode in soureData["data"]["epsodelist"]:
        episode_number = episode["order"]
        episode_name = episode["subtitle"]
        episode_air_date = episode["period"]
        duration = episode["duration"].split(':')
        episode_runtime = ""
        if len(duration) == 3:
            episode_runtime = str(int(duration[0]) * 60 + int(duration[1]))
        elif len(duration) == 2:
            episode_runtime = duration[0] 
        episode_overview = episode["description"].strip().replace("\u3002\n", "\u3002\p").replace("\uff01\n", "\uff01\p").replace("\uff1f\n", "\uff1f\p").replace("\u2026\n", "\u2026\p").replace("\u201d\n", "\u201d\p").replace("\n", "").replace("\p", "\n")
        episode_backdrop = episode["imageUrl"]

        pixel = ("0", "0")
        for imageSize in episode["imageSize"]:
            size = imageSize.split('_')
            if pixel == ("0", "0"):
                pixel =  size
            else:
                if int(size[0]) > int(pixel[0]):
                    pixel = size
        if pixel != ("0", "0"):
            episode_backdrop = episode_backdrop.rsplit(".", 1)[0] + f"_{pixel[0]}_{pixel[1]}.jpg"

        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    return episodes
