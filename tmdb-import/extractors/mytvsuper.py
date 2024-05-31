import json
import logging
import re
from ..common import Episode, open_url
from datetime import datetime

# Ex:"https://www.mytvsuper.com/tc/programme/justicesungbegins_140304/%E7%8B%80%E7%8E%8B%E4%B9%8B%E7%8E%8B/"
def mytvsuper_extractor(url):
    logging.info("mytvsuper_extractor is called")

    programme_id =  re.search(r'/programme/(.*?)/', url).group(1)
    programme_id =  programme_id.split('_')[-1]
    apiRequest = f"https://content-api.mytvsuper.com/v1/episode/list?programme_id={programme_id}&start_episode_no=1&end_episode_no=9999&platform=web"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    episodes = {}
    for episode in soureData["items"]:
        episode_number = episode["episode_no"]
        episode_name = episode["name_tc"]
        episode_air_date = episode["pay_start_time"].split("T")[0]
        episode_runtime = round(int(episode["duration"])/60)
        episode_overview = episode["desc_tc"]
        episode_backdrop = episode["image"]["large"]
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
    return episodes