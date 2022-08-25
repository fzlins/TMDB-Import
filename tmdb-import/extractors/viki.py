import json
import logging
from urllib.parse import urlparse
from ..common import Episode, open_url


# ex: https://www.viki.com/tv/37350c-a-man-in-a-veil
def viki_extractor(url, language="en-US"):
    logging.info("viki_extractor is called")
    if language=="en-US":
        language = "en"
    else:
        language = "en"

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    containerID = urlPath.rsplit('/', 1)[-1].split('-')[0]
    page = 1
    episodes = {}
    while True:
        apiRequest = f"https://api.viki.io/v4/containers/{containerID}/episodes.json?token=undefined&per_page=50&page={page}&direction=asc&sort=number&app=100000a"
        logging.debug(f"API request url: {apiRequest}")
        soureData = json.loads(open_url(apiRequest))
        for episode in soureData["response"]:
            episode_number = episode["number"]
            episode_name = ""
            episode_air_date = ""
            episode_runtime = round(episode["duration"]/60)
            if episode["descriptions"].__contains__(language):
                episode_overview = episode["descriptions"][language]
            else:
                episode_overview = ""
            episode_backdrop = episode["images"]["poster"]["url"].split("?")[0].replace("/dummy.jpg", ".jpg")
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        if (soureData["more"]):
            page = page + 1
        else:
            break

    return episodes