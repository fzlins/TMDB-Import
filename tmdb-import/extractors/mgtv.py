import json
import logging
from ..common import Episode, open_url

# language: zh
# backdrop: 860*484
# Ex:"https://w.mgtv.com/b/419629/17004788.html"
#    "https://www.mgtv.com/h/390933.html"
def mgtv_extractor(url):
    logging.info("mgtv_extractor is called")

    url = url.split('.html', 1)[0]
    
    collection_id = ""
    for part in url.split('/'):
        if (part.isdigit()):
            collection_id = part
            break
    if collection_id == "":
        return {} 
    

    page = 1
    episodes = {}
    while True:
        apiRequest = f"https://pcweb.api.mgtv.com/episode/list?_support=10000000&version=5.5.35&collection_id={collection_id}&page={page}&size=50&&callback="
        #apiRequest = f"https://pcweb.api.mgtv.com/episode/list?_support=10000000&version=5.5.35&video_id={videoID}&page=0&size=50&&callback="
        logging.debug(f"API request url: {apiRequest}")
        soureData = json.loads(open_url(apiRequest))
        for episode in soureData["data"]["list"]:
            if episode["isIntact"] == "1":
                episode_number = episode["t1"]
                episode_name = episode["t2"]
                episode_air_date = episode["ts"].split(' ')[0]
                episode_runtime = episode["time"].split(':')[0]
                episode_overview = ""
                episode_backdrop = episode["img"].rsplit('_', 1)[0]
                episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        if soureData["data"]["total_page"] == soureData["data"]["current_page"]:
            break
        else:
            page = page + 1

    return episodes