import json
import logging
from ..common import Episode
from ..common import ini_playwright_page, cleanup_playwright_page

# ex: https://www.crunchyroll.com/fr/series/GDKHZEJN0/dragon-raja--the-blazing-dawn-
def crunchyroll_extractor(url):
    logging.info("crunchyroll_extractor is called")

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

        def handle_response(response):
            if 'content/v2/cms' in response.url and response.status == 200:
                try:
                    api_responses[response.url] = json.loads(response.text())
                except:
                    pass

        api_responses = {}
        page.route('**/*', handle_route)
        page.on('response', handle_response)
        page.goto(url)
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")

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

        seasons_data = {}
        episodes_api_template = None

        for api_url, api_data in api_responses.items():
            if '/seasons' in api_url and '/episodes' not in api_url and "data" in api_data:
                for season in api_data["data"]:
                    seasons_data[season["id"]] = season
            elif '/episodes' in api_url and "data" in api_data:
                episodes_api_template = api_url

        is_multi_season = len(seasons_data) > 1

        for season_id, season in seasons_data.items():
            season_number = season.get("season_number", 1)

            if episodes_api_template:
                import re
                apiRequest = re.sub(r'/seasons/[^/]+/episodes', f'/seasons/{season_id}/episodes', episodes_api_template)
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
                            episode_backdrop = _get_episode_backdrop(episode)
                            if is_multi_season:
                                episode_key = f"S{season_number}E{episode_number}"
                            else:
                                episode_key = episode_number
                            episodes[episode_key] = Episode(episode_key, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

        if not auth_token:
            logging.warning("Could not capture Authorization token")

        logging.info(f"Extracted {len(episodes)} episodes")

    except Exception as e:
        logging.error(f"Error in crunchyroll_extractor: {e}")
    finally:
        cleanup_playwright_page(page)

    return episodes

def _get_episode_backdrop(episode):
    if "images" not in episode or "thumbnail" not in episode["images"]:
        return ""
    thumbnails = episode["images"]["thumbnail"]
    if not isinstance(thumbnails, list) or not thumbnails:
        return ""
    if isinstance(thumbnails[0], list):
        thumbnails = thumbnails[0]
    max_width = 0
    backdrop = ""
    for img in thumbnails:
        if isinstance(img, dict) and img.get("source"):
            width = img.get("width", 0)
            if width > max_width:
                max_width = width
                backdrop = img.get("source", "")
    return backdrop