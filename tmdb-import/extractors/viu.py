import json
from urllib.parse import urlparse
import logging
from ..common import Episode, open_url
from datetime import datetime

# language: zh-CN
# backdrop: 860*484
# Ex:"https://www.viu.com/ott/sg/zh-cn/vod/309897/"
def viu_extractor(url):
    logging.info("viu_extractor is called")
    
    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    product_id =  urlPath.rsplit('/', 1)[-1]
    apiRequest = f"https://www.viu.com/ott/sg/index.php?area_id=2&language_flag_id=2&r=vod/ajax-detail&platform_flag_label=web&product_id={product_id}"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    series = soureData["data"]["series"]
    season_number = 1
    season_name = series["name"]
    season_overview = series["description"]
    
    episodes = {}
    for episode in series["product"][::-1]:
        apiRequest = f"https://www.viu.com/ott/sg/index.php?area_id=2&language_flag_id=2&r=vod/ajax-detail&platform_flag_label=web&product_id={episode['product_id']}"
        logging.debug(f"API request url: {apiRequest}")
        soureData = json.loads(open_url(apiRequest))
        current_product = soureData["data"]["current_product"]
        episode_number = current_product["number"]
        episode_name = current_product["synopsis"]
        episode_air_date = datetime.fromtimestamp(int(current_product["schedule_start_time"])).date()
        episode_runtime = round(int(current_product["time_duration"])/60)
        episode_overview = current_product["description"]
        episode_backdrop = current_product["cover_image_url"]
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
    return episodes