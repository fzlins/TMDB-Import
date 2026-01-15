import json
from urllib.parse import urlparse
import logging
from ..common import Episode, open_url, ini_playwright_page, cleanup_playwright_page

# ex: https://www.hbomax.com/hk/en/shows/talking-tom-heroes-suddenly-super/55b42a25-3234-452c-a05f-5ad8a318a66e
def hbomax_extractor(url):
    logging.info("hbomax_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')
    path_parts = urlPath.split('/')
    show_id = path_parts[-1] if path_parts else ""

    if not show_id:
        logging.error("Failed to extract HBO Max show ID from URL")
        return {}

    page = None
    try:
        page = ini_playwright_page(headless=True, images=False)
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_selector("script#__NEXT_DATA__", state="attached", timeout=30000)
        next_data = page.evaluate("() => document.querySelector('#__NEXT_DATA__').textContent")
        data = json.loads(next_data)

        episodes = {}
        page_props = data.get("props", {}).get("pageProps", {})
        mapped_data = page_props.get("mappedData", {})

        if not mapped_data:
            logging.error("Failed to find mappedData in page data")
            return {}

        seasons = None
        for key, value in mapped_data.items():
            if isinstance(value, dict) and "seasons" in value:
                seasons = value.get("seasons", [])
                if isinstance(seasons, list):
                    break
                elif isinstance(seasons, dict) and "data" in seasons:
                    seasons = seasons.get("data", [])
                    break

        if not seasons:
            logging.error("Failed to find seasons data")
            return {}

        logging.debug(f"Found {len(seasons)} seasons")

        for season in seasons:
            if not isinstance(season, dict):
                continue
            season_number = season.get("seasonNumber", 1)
            episodes_data = season.get("episodes", [])
            if not isinstance(episodes_data, list):
                continue
            logging.debug(f"Season {season_number}: {len(episodes_data)} episodes")

            for ep in episodes_data:
                if not isinstance(ep, dict):
                    continue
                episode_number = ep.get("episodeNumber", "")
                if not episode_number:
                    continue

                if len(seasons) > 1:
                    episode_key = f"S{season_number}E{episode_number}"
                else:
                    episode_key = str(episode_number)

                title_obj = ep.get("title", {})
                if isinstance(title_obj, dict):
                    episode_name = title_obj.get("full", "") or title_obj.get("short", "")
                else:
                    episode_name = str(title_obj) if title_obj else ""

                summary_obj = ep.get("summary", {})
                if isinstance(summary_obj, dict):
                    episode_overview = summary_obj.get("full", "") or summary_obj.get("short", "")
                else:
                    episode_overview = str(summary_obj) if summary_obj else ""

                offering_dates = ep.get("offeringDates", {})
                if isinstance(offering_dates, dict):
                    episode_air_date = offering_dates.get("startDate", "").split("T")[0]
                else:
                    episode_air_date = ""

                episode_runtime = 0

                images = ep.get("images", {})
                if isinstance(images, dict):
                    episode_backdrop = images.get("default", "") or images.get("cover-artwork", "")
                else:
                    episode_backdrop = ""

                episodes[episode_key] = Episode(episode_key, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

        logging.info(f"Successfully extracted {len(episodes)} episodes")
        return episodes

    except Exception as e:
        logging.error(f"Failed to extract HBO Max data: {e}")
        return {}
    finally:
        if page:
            cleanup_playwright_page(page)