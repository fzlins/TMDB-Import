import json
import logging
from urllib.parse import urlparse
from ..common import Episode, open_url


# ex: https://gyao.yahoo.co.jp/store/title/267001
def yahoo_extractor(url, language="en-US"):
    logging.info("yahoo_extractor is called")
    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    title_id = urlPath.rsplit('/', 1)[-1].split('-')[0]

    episodes = {}
    apiRequest = f"https://gyao.yahoo.co.jp/store/api/titles/{title_id}/episodes?first=100&pageType=st_title"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    episode_number = 1
    for episode in soureData["singlePacks"]:
        episode_name = episode["packName"]
        if episode_name.startswith('第') and episode_name.__contains__('話'):
            episode_name = episode_name.split('話', 1)[1].strip()
        episode_air_date = ""
        episode_runtime = episode["duration"].split(":")[0]
        episode_overview = episode["storyOutlineSentence"]
        episode_backdrop = "" # to do
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episode_number = episode_number + 1

    return episodes

