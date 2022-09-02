import json
from urllib.parse import urlparse
import logging
from datetime import datetime
from ..common import Episode, open_url

def get_large_image(url):
    return str(url).replace(".xs.",".md.")

# ex: https://www.kktv.me/titles/01000577
def kktv_extractor(url):
    logging.info("kktv_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    title = urlPath.rsplit('/', 1)[-1]
    apiRequest = f"https://api.kktv.me/v3/titles/{title}"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))

    season_name = soureData["data"]["title"]
    logging.info(f"name: {season_name}")

    try:
        season_name_aliases = soureData["data"]["title_aliases"]
        for alias in season_name_aliases:
            logging.info(f"alias: {alias}")
    except:
        pass
    
    season_overview = soureData["data"]["summary"]
    logging.info(f"overview: {season_overview}")
    season_poster = get_large_image(soureData["data"]["cover"])
    logging.info(f"poster: {season_poster}")
    season_backdrop = soureData["data"]["stills"]
    for backdrop in season_backdrop:
        backdrop = get_large_image(backdrop)
        logging.info(f"backdrop: {backdrop}")
    

    episodes = {}
    episodeNumber = 1
    for episode in soureData["data"]["series"][0]["episodes"]:
        episode_number = episodeNumber
        episode_name = episode["title"]
        episode_air_date = datetime.fromtimestamp(episode["publish_time"]).date()
        episode_runtime = round(int(episode["duration"])/60)
        episode_overview = ""
        episode_backdrop = get_large_image(episode["still"])
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episodeNumber = episodeNumber + 1

    return episodes