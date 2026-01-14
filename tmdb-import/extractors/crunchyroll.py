import json
from urllib.parse import urlparse
import logging
from ..common import Episode
from ..common import ini_playwright_page, cleanup_playwright_page

# ex: https://www.crunchyroll.com/fr/series/GDKHZEJN0/dragon-raja--the-blazing-dawn-
def crunchyroll_extractor(url):
    logging.info("crunchyroll_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')
    parts = urlPath.split('/')
    
    if len(parts) >= 3 and parts[1] == 'series':
        url_language = parts[0]
        series_id = parts[2]
    else:
        url_language = 'en'
        series_id = parts[-2]
    
    if '-' in url_language:
        lang_parts = url_language.split('-')
        locale = lang_parts[0] + '-' + lang_parts[1].upper()
    else:
        locale = url_language + '-' + url_language.upper()

    episodes = {}
    auth_token = None
    max_retries = 30
    retry_delay = 2000

    page = ini_playwright_page()
    try:
        def handle_route(route):
            nonlocal auth_token
            if 'authorization' in route.request.headers:
                auth_token = route.request.headers['authorization']
            route.continue_()

        page.route('**/*', handle_route)
        page.goto(url)

        for i in range(max_retries):
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
                if auth_token:
                    break
            except:
                pass
            
            if auth_token:
                break
            
            if i < max_retries - 1:
                page.wait_for_timeout(retry_delay)

        if auth_token:
            apiRequest = f"https://www.crunchyroll.com/content/v2/cms/series/{series_id}/seasons?force_locale=&locale={locale}"
            logging.debug(f"API request url: {apiRequest}")
            response = page.request.get(apiRequest, headers={'Authorization': auth_token})
            
            if response.status == 200:
                soureData = json.loads(response.text())
                
                if "data" in soureData:
                    for season in soureData["data"]:
                        season_id = season["id"]
                        season_number = season.get("season_number", 1)

                        apiRequest = f"https://www.crunchyroll.com/content/v2/cms/seasons/{season_id}/episodes?locale={locale}"
                        logging.debug(f"API request url: {apiRequest}")
                        response = page.request.get(apiRequest, headers={'Authorization': auth_token})
                        
                        if response.status == 200:
                            episodeData = json.loads(response.text())
                            
                            if "data" in episodeData:
                                for episode in episodeData["data"]:
                                    episode_number = episode.get("episode_number", "")
                                    if not episode_number:
                                        continue
                                    episode_name = episode.get("title", "")
                                    episode_air_date = episode.get("premium_available_date", "").split("T")[0] if episode.get("premium_available_date") else ""
                                    episode_runtime = episode.get("duration_ms", 0) // 1000 // 60 if episode.get("duration_ms") else ""
                                    episode_overview = episode.get("description", "")
                                    episode_backdrop = ""
                                    
                                    if "images" in episode and "thumbnail" in episode["images"]:
                                        thumbnails = episode["images"]["thumbnail"]
                                        if isinstance(thumbnails, list) and thumbnails:
                                            if isinstance(thumbnails[0], list):
                                                thumbnails = thumbnails[0]
                                            for img in thumbnails:
                                                if isinstance(img, dict) and img.get("source"):
                                                    if img.get("width", 0) >= 1920:
                                                        episode_backdrop = img.get("source", "")
                                                        break
                                                    elif not episode_backdrop:
                                                        episode_backdrop = img.get("source", "")
                                    
                                    episode_key = f"{season_number}-{episode_number}"
                                    episodes[episode_key] = Episode(episode_key, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        else:
            logging.warning("Could not capture Authorization token")

        logging.info(f"Extracted {len(episodes)} episodes")

    finally:
        cleanup_playwright_page(page)

    return episodes