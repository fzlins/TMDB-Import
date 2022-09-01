import json
from urllib.parse import urlparse, parse_qs
import logging
from ..common import Episode, open_url
from datetime import datetime

# ex: https://www.nhk.jp/p/comecome/ts/8PMRWK3MGZ
#     https://www2.nhk.or.jp/archives/tv60bin/detail/index.cgi?das_id=D0009010034_00000#
def nhk_extractor(url):
    logging.info("nhk_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')
    if urlPath.startswith("archives"):
        urlQuery = parse_qs(urlData.query)
        das_id = urlQuery["das_id"][0].split('_', 1)[0]
        apiRequest = f"https://www.nhk.or.jp/archives/chro_data/das_rel/{das_id[0:7]}/{das_id}_00000.json"
        logging.debug(f"API request url: {apiRequest}")
        soureData = json.loads(open_url(apiRequest))
        episodes = {}
        episode_number = 1
        for episode in soureData["itemlist"]:
                episode_name = episode["title2"]
                episode_air_date = datetime.strptime(episode["airdate1"], '%Y%m%d').date()
                episode_runtime = ""
                episode_overview = episode["content"]
                episode_backdrop = ""
                episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
                episode_number = episode_number + 1
    else:
        seriesID = urlPath.rsplit('/', 1)[-1]
        nextURL = f"https://api.nhk.jp/r6/l/tvepisode/ts/{seriesID}.json?offset=0&size=100&order=asc"
        logging.debug(f"API request: {nextURL}")
        episodes = {}
        episodeNumber = 1
        while True:
            soureData = json.loads(open_url(nextURL))
            for episode in soureData["result"]:
                episode_number = episodeNumber
                episode_name = episode["name"]
                episode_air_date = episode["releasedEvent"]["startDate"].split('T')[0]
                episode_runtime = ""
                episode_overview = episode["description"]
                episode_backdrop = ""

                if episode.__contains__("eyecatch"):
                    episode_backdrop = episode["eyecatch"]["main"]["url"]
                
                episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
                episodeNumber = episodeNumber + 1

            if soureData.__contains__("nextUrl"):
                nextURL = soureData["nextUrl"]
            else:
                break
    return episodes