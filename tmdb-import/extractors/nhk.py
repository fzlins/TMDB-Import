import json
import urllib.request
from urllib.parse import urlparse
import logging
from ..common import Episode

# ex: https://www.nhk.jp/p/comecome/ts/8PMRWK3MGZ
def nhk_extractor(url):
    logging.info("nhk_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    seriesID = urlPath.rsplit('/', 1)[-1]
    nextURL = f"https://api.nhk.jp/r6/l/tvepisode/ts/{seriesID}.json?offset=0&size=100&order=asc"
    
    episodes = {}
    episodeNumber = 1
    while True:
        soureData = json.loads(urllib.request.urlopen(nextURL).read().decode('utf-8-sig'))
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