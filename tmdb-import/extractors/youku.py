import json
import logging
import re
from ..common import Episode, open_url

# ex: https://v.youku.com/v_show/id_XNDAzNzE0Mzc2MA==.html
def youku_extractor(url):
    logging.info("youku_extractor is called")
    if url.__contains__("/show_page/"):
        showID = re.search(r'id_(.*?)\.html', url).group(1).rstrip("==")
    else:
        episodeID =  re.search(r'id_(.*?)\.html', url).group(1).rstrip("==")
        apiRequest = f"https://api.youku.com/videos/show.json?video_id={episodeID}&ext=show&client_id=3d01f04416cbe807"
        # https://list.youku.com/show/module?id={showid}&tab=showInfo&callback=jQuery
        logging.debug(f"API request url: {apiRequest}")
        videoData = json.loads(open_url(apiRequest))
        showID = videoData["show"]["id"]
    logging.info(f"show id: {showID}")
    apiRequest = f"https://openapi.youku.com/v2/shows/show.json?show_id={showID}&&client_id=3d01f04416cbe807"
    logging.debug(f"API request url: {apiRequest}")
    show_data = json.loads(open_url(apiRequest))
    season_link = show_data["link"]
    logging.info(f"show link: {season_link}")
    season_name = show_data["name"]
    logging.info(f"name: {season_name}")
    season_poster = show_data["poster_large"]
    logging.info(f"poster url: {season_poster}")
    season_backdrop = show_data["thumbnail_large"]
    logging.info(f"backdrop url: {season_backdrop}")
    season_description = show_data["description"]
    logging.info(f"description url: {season_description}")
    
    page = 1
    episodeNumber = 1
    total = 0
    episodes =  {}
    while True:
        apiRequest = f"https://openapi.youku.com/v2/shows/videos.json?show_id={showID}&show_videotype=%E6%AD%A3%E7%89%87&page={page}&count=30&client_id=3d01f04416cbe807"
        logging.debug(f"API request url: {apiRequest}")
        showData = json.loads(open_url(apiRequest))
        if total == 0:
            total = int(showData["total"])

        for episode in showData["videos"]:
            episodeID = episode["id"].strip("==")
            try:
                apiRequest = f"https://api.youku.com/videos/show.json?video_id={episodeID}&client_id=3d01f04416cbe807"
                logging.debug(f"API request url: {apiRequest}")
                videoData = json.loads(open_url(apiRequest))

                episode_number = episodeNumber
                episode_name = ""
                episode_air_date = videoData["published"].split(" ")[0]
                episode_runtime = round(float(videoData["duration"])/60)
                episode_overview = videoData["description"]
                episode_backdrop = videoData["bigThumbnail"][0:23] + "F" + videoData["bigThumbnail"][24:]
                episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
            except Exception as err:
                logging.error(err)

            episodeNumber = episodeNumber + 1

        if page * 30 > total:
            break
        else:
            page = page + 1

    return episodes