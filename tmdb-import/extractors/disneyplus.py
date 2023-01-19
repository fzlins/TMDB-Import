import json
from urllib.parse import urlparse
import logging
from ..common import Episode, open_url

# ex: https://www.disneyplus.com/zh-hans/series/big-mouth/7kIy3S1m2HNY
def disneyplus_extractor(url, language="zh-CN"): 
    logging.info("disneyplus_extractor is called")

    if language == "zh-CN":
        language = "zh-Hans"
        region = "sg"
    else: # default "zh-Hans"
        language = "zh-Hans"
        region = "sg"

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')
    seriesID = urlPath.rsplit("/", 1)[-1]
    apiRequest = f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/{region}/audience/false/maturity/1850/language/{language}/encodedSeriesId/{seriesID}"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))

    season_name = soureData["data"]["DmcSeriesBundle"]["series"]["text"]["title"]["full"]["series"]["default"]["content"]
    logging.info(f"name: {season_name}")
    season_overview = soureData["data"]["DmcSeriesBundle"]["series"]["text"]["description"]["full"]["series"]["default"]["content"]
    logging.info(f"overview: {season_overview}")
    season_poster = soureData["data"]["DmcSeriesBundle"]["series"]["image"]["tile"]["0.71"]["series"]["default"]["url"]
    logging.info(f"poster: {season_poster}")
    season_backdrop = soureData["data"]["DmcSeriesBundle"]["series"]["image"]["tile"]["1.78"]["series"]["default"]["url"]
    logging.info(f"season_backdrop: {season_backdrop}")
    season_logo = soureData["data"]["DmcSeriesBundle"]["series"]["image"]["title_treatment_centered"]["1.78"]["series"]["default"]["url"]
    logging.info(f"season_backdrop: {season_logo}")

    episodes = {}
    for season in soureData["data"]["DmcSeriesBundle"]["seasons"]["seasons"]:
        season_number = season["seasonSequenceNumber"]
        hits = season["episodes_meta"]["hits"]
        seasonId = season["seasonId"]
        apiRequest = f"https://disney.content.edge.bamgrid.com/svc/content/DmcEpisodes/version/5.1/region/{region}/audience/false/maturity/1850/language/{language}/seasonId/{seasonId}/pageSize/60/page/1"
        logging.debug(f"API request url: {apiRequest}")
        soureData = json.loads(open_url(apiRequest))

        for episode in soureData["data"]["DmcEpisodes"]["videos"]:
            episode_number = f"S{season_number}E{episode['episodeSequenceNumber']}"
            episode_name = episode["text"]["title"]["full"]["program"]["default"]["content"]
            episode_air_date = episode["releases"][0]["releaseDate"]
            episode_runtime = round(episode["mediaMetadata"]["runtimeMillis"]/60000)
            episode_overview = episode["text"]["description"]["full"]["program"]["default"]["content"]
            episode_backdrop = episode["image"]["thumbnail"]["1.78"]["program"]["default"]["url"]
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    return episodes