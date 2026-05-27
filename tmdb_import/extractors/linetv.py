import json
from urllib.parse import urlparse
import logging
import re
from ..common import Episode, Metadata, Season, open_url

# ex: https://www.linetv.tw/drama/15566 or https://www.linetv.tw/drama/18009/eps/1
def linetv_extractor(url):
    logging.info("linetv_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path

    # Extract drama ID from URL path using regex
    # Matches patterns like /drama/15566 or /drama/18009/eps/1
    match = re.search(r'/drama/(\d+)', urlPath)
    if not match:
        logging.error(f"Could not extract drama ID from URL: {url}")
        return Metadata(url=url, seasons=[])
    
    drama_id = match.group(1)
    logging.info(f"Extracted drama_id: {drama_id}")
    
    # API request to get drama info
    apiRequest = f"https://www.linetv.tw/api/dramaInfo/{drama_id}"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))

    # Extract drama info
    season_name = soureData.get("drama_name", "")
    logging.info(f"name: {season_name}")
    
    # Extract show-level metadata
    season_overview = None
    season_backdrop = None
    season_poster = None
    
    # Extract and log description
    if "introduction" in soureData:
        season_overview = soureData["introduction"]
        logging.info(f"overview: {season_overview}")
    
    # Extract and log backdrop (horizontal poster)
    if "horizontal_poster_url" in soureData:
        season_backdrop = soureData["horizontal_poster_url"].replace("/medium/", "/large/")
        logging.info(f"backdrop: {season_backdrop}")
    
    # Extract and log poster (vertical poster)
    if "vertical_poster_url" in soureData:
        season_poster = soureData["vertical_poster_url"].replace("/medium/", "/large/")
        logging.info(f"poster: {season_poster}")

    episodes = {}
    
    # Extract episode data - use eps_info instead of episodes
    if "eps_info" in soureData and soureData["eps_info"]:
        for episode in soureData["eps_info"]:
            episode_number = episode.get("number", 0)
            episode_name = episode.get("title", "")
            
            # Parse air date - not available in this API
            episode_air_date = ""
            
            # Parse duration (convert milliseconds to minutes)
            episode_runtime = ""
            if "durationInMs" in episode:
                # Convert milliseconds to minutes
                episode_runtime = str(round(int(episode["durationInMs"]) / 60000))
            
            episode_overview = ""  # Not available in episode data
            episode_backdrop = ""  # Not available in episode data
            
            episodes[episode_number] = Episode(
                episode_number, 
                episode_name, 
                episode_air_date, 
                episode_runtime, 
                episode_overview, 
                episode_backdrop
            )
    
    logging.info(f"Total episodes found: {len(episodes)}")
    return Metadata(
        url=url, 
        language="zh-TW", 
        title=season_name, 
        overview=season_overview,
        poster=season_poster,
        backdrop=season_backdrop,
        seasons=[Season(None, episodes=episodes)]
    )
