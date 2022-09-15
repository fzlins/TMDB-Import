import json
import logging
from ..common import Episode, open_url
from datetime import datetime
from urllib.parse import urlparse
import re
# cctv 4k
# ex: https://tv.cctv.com/2020/09/07/VIDEFozlyfO7mjXUP2sNidVi200907.shtml
def cctv_extractor(url):
    logging.info("cctv_extractor is called")
    
    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    guid = urlPath.rsplit('/', 1)[-1].split('.', 1)[0]
    if guid.startswith('VIDA'):
        albumId = guid
    else:        
        webPage = open_url(url)
        guid = re.search(r'guid_Ad_VideoCode(.*?);', str(webPage)).group(1)
        guid = guid.replace('=', "").strip().strip('\"')
        if len(guid) < 20:
            guid = re.search(r'guid (.*?);', str(webPage)).group(1)
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
    episode_number = 1
    for episode in soureData["data"]["list"]:
        try:
            episode_name = episode["title"].split('集', 1)[1].strip()
        except:
            episode_name = episode["title"].split('》', 1)[1].strip()

        try:
            air_date = ''.join(filter(str.isdigit, episode["title"].split('集', 1)[0]))
            episode_air_date = datetime.strptime(air_date, '%Y%m%d').date()
        except:    
            episode_air_date = ""

        time_length = episode["length"].split(":")
        episode_runtime = int(time_length[0])*60 + int(time_length[1])
        episode_overview = episode["brief"].replace("（" + episode["title"] + "）", "")
        if episode_overview.__contains__("主要内容："):
            episode_overview = episode_overview.split('：', 1)[1].strip()
        episode_backdrop = episode["image"]
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episode_number = episode_number + 1

    return episodes