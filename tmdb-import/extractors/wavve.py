import json
import logging
import re
from ..common import Episode, open_url

# language: kr
# backdrop: 1280*720
# Ex:"https://www.wavve.com/player/vod?programid=H04_SP0000054887&page=1"
def wavve_extractor(url):
    logging.info("wavve_extractor is called")
    programid = re.search(r'programid=(.*?)[\&$]', str(url)).group(1)
    apiRequest = f"https://apis.wavve.com/fz/vod/programs-contents/{programid}?limit=50&offset=0&orderby=old&apikey=E5F3E0D30947AA5440556471321BB6D9&credential=none&device=pc&drm=wm&partner=pooq&pooqzone=none&region=kor&targetage=all"
    logging.debug(f"API request url: {apiRequest}")
    sourceData = json.loads(open_url(apiRequest))
    episodes = {}
    episode_number = 1
    for episode in sourceData["cell_toplist"]["celllist"]:
        episode_name = episode["title_list"][0]["text"]
        episode_air_date = episode["title_list"][1]["text"].rsplit(' ', 1)[-1].split("(")[0]
        episode_runtime = round(int(episode["_playtime_log"].split(',')[0])/60)
        episode_overview = episode["synopsis"]
        episode_backdrop = f"https://{episode['thumbnail']}"
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episode_number = episode_number + 1 
    return episodes