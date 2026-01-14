import json
from urllib.parse import urlparse
import logging
from ..common import Episode, open_url

# ex: https://www.tvbanywhere.com/en/webtv/programme/thequeenofnews2_144840/766522/The-QUEEN-Of-News
def tvbanywhere_extractor(url, language="zh-CN"):
    logging.info("tvbanywhere_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    path_parts = urlPath.split('/')
    programme_id = None
    for part in path_parts:
        if '_' in part:
            programme_id = part.split('_')[-1]
            break

    if not programme_id:
        for part in path_parts:
            if part.isdigit() and len(part) > 3:
                programme_id = part
                break

    if not programme_id:
        logging.error("Failed to extract programme_id from URL")
        return {}

    logging.info(f"programme_id: {programme_id}")

    if '/en/' in url:
        lang_code = 'en'
    elif '/tc/' in url:
        lang_code = 'tc'
    elif '/sc/' in url:
        lang_code = 'sc'
    else:
        lang_code = 'en'

    apiRequest = f"https://apisfm.tvbanywhere.com.sg/programme/US/webtv/{lang_code}/{programme_id}.json"
    logging.debug(f"API request url: {apiRequest}")

    try:
        soureData = json.loads(open_url(apiRequest))
    except Exception as e:
        logging.error(f"Failed to request TVB Anywhere API: {e}")
        return {}

    episodes = {}

    programme_name = soureData.get('programme_name', '')
    programme_desc = soureData.get('programme_desc', '')
    total_episodes = soureData.get('no_of_episode', 0)

    logging.info(f"name: {programme_name}")
    logging.info(f"overview: {programme_desc[:100]}...")
    logging.info(f"total episodes: {total_episodes}")

    episode_api_url = f"https://apisfm.tvbanywhere.com.sg/episode/list/country_code/US/platform/webtv/language/{lang_code}/programme_id/{programme_id}/offset/0/limit/100"
    logging.debug(f"Episode API request url: {episode_api_url}")

    try:
        episode_data = json.loads(open_url(episode_api_url))
        episode_list = episode_data.get('episodes', [])

        for ep in episode_list:
            episode_number = ep.get('episode_no', 0)
            episode_name = ep.get('episode_name', '')
            episode_overview = ep.get('synopsis', '')
            episode_runtime = round(ep.get('duration', 0) / 60)
            episode_air_date = ep.get('start_time', '').split('T')[0] if ep.get('start_time') else ''

            episode_images = ep.get('episode_images', [])
            episode_backdrop = ''
            if episode_images:
                episode_backdrop = episode_images[0].get('image_path', '')

            if episode_number > 0:
                episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

        logging.info(f"Successfully extracted {len(episodes)} episodes")

    except Exception as e:
        logging.error(f"Failed to get episode list: {e}")

    return episodes