import json
import logging
from datetime import datetime
from urllib.parse import urlparse
from ..common import Episode, Metadata, Season, open_url

# ex: https://douga.tv-asahi.co.jp/program/24583-24582/24590?auto=t
def asahi_extractor(url):
    logging.info("asahi_extractor is called")
    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    program_id = urlPath.split('/')[1].split('-', 1)[0]
    apiRequest = f'https://douga.tv-asahi.co.jp/pathEvaluator?paths=[["meta","children","{program_id}"]]&method=get'
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))

    children = soureData["jsonGraph"]["meta"]["children"][program_id]["value"]

    season_map = {}
    for season_data in children:
        if season_data['meta_schema_id'] != 3:
            continue

        season_number = season_data['values'].get('avails_SeasonNumber')
        logging.info(f"season: {season_number}")
        season_name = season_data['values'].get('evis_FrontDisplayTitle')
        logging.info(f"name: {season_name}")
        season_catchphrase = season_data['values'].get('evis_Catchphrase')
        logging.info(f"catchphrase: {season_catchphrase}")
        season_overview = season_data['values'].get('evis_SeasonLongSynopsis')
        logging.info(f"overview: {season_overview}")
        season_backdrop = season_data.get('thumbnail_url')
        logging.info(f"backdrop: {season_backdrop}")

        season_obj = Season(
            season_number=season_number,
            title=season_name,
            overview=season_overview,
            poster=season_backdrop,
            episodes={},
        )
        season_map[season_data['id']] = season_obj

    if not season_map:
        season_map["__default__"] = Season(season_number=None, episodes={})

    for episode in children:
        if episode['meta_schema_id'] != 7:
            continue

        episode_number = episode['values'].get('avails_EpisodeNumber')

        if len(season_map) > 1:
            season_id = episode['values']['parents_season']['id']
            season_obj = season_map.get(season_id)
            if season_obj is None:
                season_obj = season_map.setdefault("__fallback__", Season(season_number=None, episodes={}))
        else:
            season_obj = next(iter(season_map.values()))

        episode_name = episode['values']['avails_EpisodeTitleDisplayUnlimited'].rstrip('[字幕]').lstrip(f"＃{episode_number}　")
        episode_air_date = datetime.strptime(episode['publish_start_at'], '%Y/%m/%d %H:%M:%S').date()
        episode_runtime = round(episode['values']["duration"]/60)
        episode_overview = episode['values']["evis_EpisodeLongSynopsis"]
        episode_backdrop = episode['thumbnail_url']

        season_obj.episodes[episode_number] = Episode(
            episode_number,
            episode_name,
            episode_air_date,
            episode_runtime,
            episode_overview,
            episode_backdrop,
        )

    season_list = sorted(
        season_map.values(),
        key=lambda s: (s.season_number is None, s.season_number),
    )
    return Metadata(url=url, language="ja-JP", seasons=season_list)

def get_larger_image(image):
    image_heght = image["height"]
    image_width = image["width"]
    image_url = image["url"]
    return image_url.format(w=image_width, h=image_heght, f="jpg")