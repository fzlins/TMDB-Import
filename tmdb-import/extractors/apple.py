import json
import logging
from urllib.parse import urlparse
from ..common import Episode, open_url
from datetime import datetime

# ex: https://tv.apple.com/sg/show/surfside-girls/umc.cmc.4371g2xacdr0wfs071dm3q30x?ctx_brand=tvs.sbd.4000&l=ZHS
# ex: https://tv.apple.com/us/movie/three-thousand-years-of-longing/umc.cmc.2ya70jyatuz8iuzr05vt5t8ve
def apple_extractor(url):
    logging.info("apple_extractor is called")
    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    country = urlPath.split('/', 1)[0]
    if country == "jp":
        location = "ja-JP"
        sf = "143462"
    elif country == "kr":
        location = "ko-KR"
        sf= "143466"
    elif country == "gb":
        location = "en-GB"
        sf = "143444"
    elif country == "us":
        location = "en-US"
        sf = "143441"
    else:
        location = "cmn_Hans"
        sf = "143464"

    guid = urlPath.rsplit('/', 1)[-1]
    if urlPath.__contains__("/shows/") or urlPath.__contains__("/show/"):
        apiRequest = f"https://tv.apple.com/api/uts/v3/shows/{guid}?caller=web&sf={sf}&v=58&pfm=web&locale={location}&utsk=AAAAAAAAA"
        logging.debug(f"API request url: {apiRequest}")
        soureData = json.loads(open_url(apiRequest))

        season_name = soureData["data"]["content"]["title"]
        logging.info(f"name: {season_name}")
        season_overview = soureData["data"]["content"]["description"]
        logging.info(f"overview: {season_overview}")
        try:
            season_poster = get_larger_image(soureData["data"]["content"]["images"]["contentImageTall"])
            logging.info(f"poster: {season_poster}")
        except:
            pass
        try:
            season_backdrop = get_larger_image(soureData["data"]["content"]["images"]["contentImage"])
            logging.info(f"backdrop: {season_backdrop}")
        except:
            pass
        try:
            season_backdrop = get_larger_image(soureData["data"]["content"]["images"]["posterArt"])
            logging.info(f"backdrop: {season_backdrop}")
        except:
            pass
        try:
            season_logo = get_larger_image(soureData["data"]["content"]["images"]["contentLogo"])
            logging.info(f"logo: {season_logo}")
        except:
            pass

        apiRequest = f"https://tv.apple.com/api/uts/v3/shows/{guid}/episodes?caller=web&sf={sf}&v=58&pfm=web&locale={location}&nextToken=0:999&includeSeasonSummary=false&selectedSeasonEpisodesOnly=true&utsk=AAAAAAAAA"
        logging.debug(f"API request url: {apiRequest}")
        soureData = json.loads(open_url(apiRequest))
        episodes = {}
        for episode in soureData["data"]["episodes"]:
            episode_number = f"S{episode['seasonNumber']}E{episode['episodeNumber']}"
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
    elif urlPath.__contains__("/movie/"):
        apiRequest = f"https://tv.apple.com/api/uts/v3/movies/{guid}?caller=web&sf={sf}&v=58&pfm=web&locale={location}&utsk=AAAAAAAAA"
        logging.debug(f"API request url: {apiRequest}")
        soureData = json.loads(open_url(apiRequest))
        movie_name = soureData["data"]["content"]["title"]
        logging.info(f"name: {movie_name}")
        movie_overview = soureData["data"]["content"]["description"]
        logging.info(f"overview: {movie_overview}")
        try:
            movie_poster = get_larger_image(soureData["data"]["content"]["images"]["contentImageTall"])
            logging.info(f"poster: {movie_poster}")
        except:
            pass
        try:
            movie_backdrop = get_larger_image(soureData["data"]["content"]["images"]["contentImage"])
            logging.info(f"backdrop: {movie_backdrop}")
        except:
            pass
        try:
            movie_backdrop = get_larger_image(soureData["data"]["content"]["images"]["posterArt"])
            logging.info(f"backdrop: {movie_backdrop}")
        except:
            pass
        try:
            movie_logo = get_larger_image(soureData["data"]["content"]["images"]["contentLogo"])
            logging.info(f"logo: {movie_logo}")
        except:
            pass

        movie_runtime = round(soureData["data"]["content"]["duration"]/60)
        logging.info(f"runtime: {movie_runtime}")

        movie_air_date = datetime.fromtimestamp(soureData["data"]["content"]["releaseDate"]/1000).date()
        logging.info(f"runtime: {movie_air_date}")

    return {}

def get_larger_image(image):
    image_heght = image["height"]
    image_width = image["width"]
    image_url = image["url"]
    return image_url.format(w=image_width, h=image_heght, f="jpg")