import json
import logging
from urllib.parse import urlparse
from ..common import Episode, open_url
from datetime import datetime

# ex: https://douga.tv-asahi.co.jp/program/24583-24582/24590?auto=t
def asahi_extractor(url):
    logging.info("asahi_extractor is called")
    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    program_id = urlPath.split('/')[1].split('-', 1)[0]
    apiRequest = f'https://douga.tv-asahi.co.jp/pathEvaluator?paths=[["meta","children","{program_id}"]]&method=get'
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    
    seasons = {}
    for season in soureData["jsonGraph"]["meta"]["children"][program_id]["value"]:
        if season['meta_schema_id'] != 3:
            continue

        season_number = season['values']['avails_SeasonNumber']
        logging.info(f"season: {season_number}")
        season_name = season['values']['evis_FrontDisplayTitle']
        logging.info(f"name: {season_name}")
        season_catchphrase = season['values']['evis_Catchphrase']
        logging.info(f"catchphrase: {season_catchphrase}")
        season_overview = season['values']['evis_SeasonLongSynopsis']
        logging.info(f"overview: {season_overview}")
        season_backdrop = season['thumbnail_url']
        logging.info(f"backdrop: {season_backdrop}")
        seasons[season['id']] = season_number
        logging.info(f"backdrop: {season_backdrop}")

    episodes = {}
    for episode in soureData["jsonGraph"]["meta"]["children"][program_id]["value"]:
        if episode['meta_schema_id'] != 7:
            continue
        if len(seasons) > 1:
            season_id = episode['values']['parents_season']['id']
            season_number = seasons[season_id]
            episode_number = f"S{season_number}E{episode['values']['avails_EpisodeNumber']}"
        else:
            episode_number = episode['values']['avails_EpisodeNumber']

        episode_name = episode['values']['avails_EpisodeTitleDisplayUnlimited'].rstrip('[字幕]').lstrip(f"＃{episode_number}　")
        episode_air_date = datetime.strptime(episode['publish_start_at'], '%Y/%m/%d %H:%M:%S').date()
        episode_runtime = round(episode['values']["duration"]/60)
        episode_overview = episode['values']["evis_EpisodeLongSynopsis"]
        episode_backdrop = episode['thumbnail_url']
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    return episodes

def get_larger_image(image):
    image_heght = image["height"]
    image_width = image["width"]
    image_url = image["url"]
    return image_url.format(w=image_width, h=image_heght, f="jpg")