import json
import urllib.request
import logging
from ..common import Episode

# ex: https://www.disneyplus.com/zh-hans/series/big-mouth/7kIy3S1m2HNY
def disneyplus_extractor(url, language="zh-CN"): 
    logging.info("disneyplus_extractor is detected")
    
    if language == "zh-CN":
        language == "zh-Hans"
    else: # default "zh-Hans"
        language = "zh-Hans"

    seriesID = url.split("?")[0].rsplit('/', 1)[-1]
    apiRequest = f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/SG/audience/false/maturity/1850/language/{language}/encodedSeriesId/{seriesID}"
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode('utf-8-sig'))
    episodes = {}
    for episode in soureData["data"]["DmcSeriesBundle"]["episodes"]["videos"]:
        episode_number = episode["episodeSequenceNumber"]
        episode_name = episode["text"]["title"]["full"]["program"]["default"]["content"]
        episode_air_date = episode["releases"][0]["releaseDate"]
        episode_runtime = round(episode["mediaMetadata"]["runtimeMillis"]/60000)
        episode_overview = episode["text"]["description"]["full"]["program"]["default"]["content"]
        episode_backdrop = episode["image"]["thumbnail"]["1.78"]["program"]["default"]["url"]
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    return episodes