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
    
    if len(parts) >= 3 and parts[1] == 'series' and parts[0] in ['ar', 'de', 'en', 'es', 'fr', 'it', 'pt', 'ru']:
        url_language = parts[0]
        series_id = parts[2]
    else:
        url_language = 'en'
        series_id = parts[-2]
    
    locale = 'en-US' if url_language == 'en' else 'pt-BR' if url_language == 'pt' else 'ar-SA' if url_language == 'ar' else url_language + '-' + url_language.upper()

    episodes = {}
    auth_token = None

    page = ini_playwright_page()
    try:
        def handle_route(route):
            nonlocal auth_token
            if 'authorization' in route.request.headers:
                auth_token = route.request.headers['authorization']
            route.continue_()

        page.route('**/*', handle_route)
        page.goto(url)
        page.wait_for_load_state("networkidle", timeout=30000)

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