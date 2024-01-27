import json
import logging
import re
from datetime import datetime
import pytz
from ..common import Episode, open_url

# language: zh
# Ex:"https://www.iqiyi.com/v_ik3832z0go.html"
def iqiyi_extractor(url):
    logging.info("iqiyi_extractor is called")
    webPage = open_url(url)
    if url.__contains__("iqiyi.com/lib/m_"):
        albumId = re.search(r'movlibalbumaid=\"(.*?)\"', str(webPage)).group(1)
    else:
        albumId = re.search(r'\"albumId\":(.*?),', str(webPage)).group(1)
        albumId = albumId[:-1] + "1"
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
        episode_air_date = datetime.fromtimestamp(episode["issueTime"]/1000, pytz.timezone("ETC/GMT-8")).date()
        duration = episode["duration"].split(':')
        episode_runtime = ""
        if len(duration) == 3:
            episode_runtime = str(int(duration[0]) * 60 + int(duration[1]))
        elif len(duration) == 2:
            episode_runtime = duration[0] 
        episode_overview = episode["description"]
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