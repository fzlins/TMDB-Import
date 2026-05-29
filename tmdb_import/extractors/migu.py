import json
import logging
import re
from ..common import Episode, Metadata, Season, open_url

# language: zh-CN
# Ex: "https://www.miguvideo.com/p/detail/965011629"
def migu_extractor(url):
    logging.info("migu_extractor is called")
    
    # Extract pID from URL
    pid_match = re.search(r'/detail/(\d+)', url)
    if not pid_match:
        logging.error("Could not extract pID from URL")
        return Metadata(url=url, seasons=[])
    
    pid = pid_match.group(1)
    logging.debug(f"Extracted pID: {pid}")
    
    # Fetch detail page data using program-dynamic API
    # This API returns data for a specific episode, but includes the full episode list in datas field
    api_url = f"https://webapi.miguvideo.com/gateway/program-dynamic/v4/cont/dynamic-cdn/{pid}/1"
    logging.debug(f"API request url: {api_url}")
    
    try:
        response_data = json.loads(open_url(api_url))
        
        if response_data.get("code") != 200:
            logging.error(f"API returned error code: {response_data.get('code')}")
            return Metadata(url=url, seasons=[])
        
        data = response_data.get("body", {}).get("data", {})
        
        # Extract show metadata
        title = data.get("name", "")
        overview = data.get("detail", "")
        epsCount = data.get("epsCount", 0)
        year = data.get("year", "")
        
        logging.info(f"Title: {title}")
        logging.info(f"Total episodes: {epsCount}")
        
        # Extract episodes from datas array
        episodes = {}
        datas = data.get("datas", [])
        
        if isinstance(datas, list) and datas:
            episode_number = 1
            for ep_data in datas:
                # Skip previews/trailers (isPrevue == "1")
                if ep_data.get("isPrevue") == "1":
                    logging.debug(f"Skipping preview: {ep_data.get('name', '')}")
                    continue
                
                # Extract episode name - split by "：" or ":" and take the part after it
                episode_name = ep_data.get("name", "")
                if "：" in episode_name:
                    episode_name = episode_name.split("：", 1)[1].strip()
                elif ":" in episode_name:
                    episode_name = episode_name.split(":", 1)[1].strip()
                
                # Extract duration in format "46:18" or "01:04:04" and convert to minutes
                episode_duration = ep_data.get("duration", "00:00")
                try:
                    parts = episode_duration.split(":")
                    if len(parts) == 3:
                        # Format: HH:MM:SS
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        episode_runtime = str(hours * 60 + minutes)
                    elif len(parts) >= 2:
                        # Format: MM:SS
                        episode_runtime = str(int(parts[0]))
                    else:
                        episode_runtime = ""
                except:
                    episode_runtime = ""
                
                # Get episode detail/overview
                episode_overview = ep_data.get("detail", "")
                
                # Air date is not directly available in episode data, use "null"
                episode_air_date = "null"
                
                episodes[episode_number] = Episode(
                    episode_number, 
                    episode_name, 
                    episode_air_date, 
                    episode_runtime, 
                    episode_overview, 
                    ""  # No backdrop
                )
                
                episode_number += 1
            
            logging.info(f"Successfully extracted {len(episodes)} episodes")
        
        return Metadata(
            url=url, 
            language="zh-CN", 
            title=title, 
            overview=overview,
            release_date=year,
            seasons=[Season(None, episodes=episodes)]
        )
        
    except Exception as e:
        logging.error(f"Error fetching migu data: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        return Metadata(url=url, seasons=[])
