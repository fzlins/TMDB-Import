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
        albumId = re.search(r'movlibalbumaid=\"(.*?)\"', str(webPage)).group(1)
    else:
        albumId = re.search(r'\"albumId\":(.*?),', str(webPage)).group(1)
    apiRequest = f"https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={albumId}&page=1&size=999&callback="
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    episodes = {}
    for episode in soureData["data"]["epsodelist"]:
        episode_number = episode["order"]
        episode_name = episode["subtitle"]
        episode_air_date = datetime.fromtimestamp(episode["publishTime"]/1000).date()
        episode_runtime = episode["duration"].split(':')[0]
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
            episode_backdrop = episode_backdrop.rsplit(".", 1)[0] + f"_imageWidth_imageHeight.jpg?imageWidth={pixel[0]}&imageHeight={pixel[1]}"

        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    return episodes