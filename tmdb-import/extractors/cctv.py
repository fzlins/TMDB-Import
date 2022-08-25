import json
import logging
from ..common import Episode, open_url
import re
# cctv 4k
# ex: https://tv.cctv.com/2020/09/07/VIDEFozlyfO7mjXUP2sNidVi200907.shtml
def cctv_extractor(url):
    logging.info("cctv_extractor is called")
    
    webPage = open_url(url)
    guid = re.search(r'guid_Ad_VideoCode(.*?);', str(webPage)).group(1)
    guid = guid.replace('=', "").strip().strip('\"')
    apiRequest = f"https://api.cntv.cn/video/videoinfoByGuid?serviceId=cctv4k&guid={guid}&t=jsonp&cb=Callback"
    logging.debug(f"API request url: {apiRequest}")
    webPage = open_url(apiRequest)
    albumId = re.search(r'\"album_ids\":(.*?),', str(webPage)).group(1)
    albumId = albumId.strip('\"')
    apiRequest = f"https://api.cntv.cn/NewVideo/getVideoListByAlbumIdNew?id={albumId}&serviceId=cctv4k&p=1&n=100&sort=asc&mode=0&pub=2&cb="
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    episodes = {}
    episodeNumber = 1
    for episode in soureData["data"]["list"]:
        episode_number = episode["part"]
        episode_name = "" #episode["title"]
        episode_air_date = ""
        time_length = episode["length"].split(":")
        episode_runtime = int(time_length[0])*60 + int(time_length[1])
        episode_overview = episode["brief"].replace("本集主要内容：", "").replace("（" + episode["title"] + "）", "")
        episode_backdrop = episode["image"]
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episodeNumber = episodeNumber + 1

    return episodes