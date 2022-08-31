import json
import logging
from urllib.parse import urlparse
from ..common import Episode, open_url
from datetime import datetime

# ex: https://tv.apple.com/sg/show/surfside-girls/umc.cmc.4371g2xacdr0wfs071dm3q30x?ctx_brand=tvs.sbd.4000&l=ZHS
def apple_extractor(url):
    logging.info("apple_extractor is called")
    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    country = urlPath.split('/', 1)[0]
    if country == "jp":
        location = "ja-JP"
        sf = "143462"
    else:
        location = "cmn_Hans"
        sf = "143464"

    show_id = urlPath.rsplit('/', 1)[-1]

    apiRequest = f"https://tv.apple.com/api/uts/v3/shows/{show_id}?caller=web&sf={sf}&v=58&pfm=web&locale={location}"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))

    season_name = soureData["data"]["content"]["title"]
    logging.info(f"name: {season_name}")
    season_overview = soureData["data"]["content"]["description"]
    logging.info(f"overview: {season_overview}")
    season_poster = get_larger_image(soureData["data"]["content"]["images"]["contentImageTall"])
    logging.info(f"poster: {season_poster}")
    season_backdrop = get_larger_image(soureData["data"]["content"]["images"]["contentImage"])
    logging.info(f"backdrop: {season_backdrop}")
    season_backdrop = get_larger_image(soureData["data"]["content"]["images"]["posterArt"])
    logging.info(f"backdrop: {season_backdrop}")
    season_logo = get_larger_image(soureData["data"]["content"]["images"]["contentLogo"])
    logging.info(f"logo: {season_logo}")

    apiRequest = f"https://tv.apple.com/api/uts/v3/shows/{show_id}/episodes?caller=web&sf={sf}&v=58&pfm=web&locale={location}&nextToken=0:99&includeSeasonSummary=false&selectedSeasonEpisodesOnly=true"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    episodes = {}
    for episode in soureData["data"]["episodes"]:
        episode_number = episode["episodeNumber"]
        episode_name = episode["title"]
        episode_air_date = datetime.fromtimestamp(episode["releaseDate"]/1000).date()
        episode_runtime = round(episode["duration"]/60)
        try:
            episode_overview = episode["description"]
        except:
            episode_overview = ""
        episode_backdrop = get_larger_image(episode["images"]["posterArt"])
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    return episodes

def get_larger_image(image):
    image_heght = image["height"]
    image_width = image["width"]
    image_url = image["url"]
    return image_url.format(w=image_width, h=image_heght, f="jpg")