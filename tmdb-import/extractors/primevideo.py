import json
import logging
import re
from datetime import datetime
from ..common import Episode, ini_playwright_page, cleanup_playwright_page

# ex: https://www.amazon.co.jp/%E7%AC%AC02%E8%A9%B1/dp/B07TRLY369/
def primevideo_extractor(url):
    logging.info("primevideo_extractor is called")
    
    page = None
    episodes = {}
    
    try:
        page = ini_playwright_page(headless=True, images=False)
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        try:
            episode_expander = page.locator("a[data-automation-id='ep-expander']")
            if episode_expander.count() > 0:
                href = episode_expander.get_attribute("href")
                if href:
                    page.goto(href)
        except:
            pass
        
        scripts = page.locator("script").all()
        episode_data = {}
        
        for script in scripts:
            try:
                content = script.text_content()
                if content and len(content) > 1000:
                    data = json.loads(content)
                    for item in data.get("props", {}).get("body", []):
                        if isinstance(item, dict):
                            detail_obj = item.get("props", {}).get("btf", {}).get("state", {}).get("detail", {}).get("detail", {})
                            if isinstance(detail_obj, dict):
                                for title_id, title_data in detail_obj.items():
                                    if isinstance(title_data, dict) and title_data.get("episodeNumber"):
                                        episode_data[title_id] = title_data
                                if episode_data:
                                    break
            except:
                continue
        
        if episode_data:
            for title_id, ep_data in episode_data.items():
                episode_number = ep_data.get("episodeNumber", "")
                if not episode_number:
                    continue
                
                episode_name = ep_data.get("title", "")
                episode_air_date = ep_data.get("releaseDate", "")
                if episode_air_date:
                    try:
                        if "年" in episode_air_date:
                            episode_air_date = episode_air_date.replace("年", "-").replace("月", "-").replace("日", "")
                        episode_air_date = datetime.strptime(episode_air_date, '%Y-%m-%d').date()
                    except:
                        episode_air_date = ""
                
                episode_runtime = ep_data.get("runtime", "")
                if episode_runtime:
                    match = re.search(r'(\d+)\s*(分|分钟|min)', episode_runtime)
                    if match:
                        episode_runtime = int(match.group(1))
                    else:
                        episode_runtime = ""
                
                episode_overview = ep_data.get("synopsis", "")
                images = ep_data.get("images", {})
                episode_backdrop = images.get("packshot") or images.get("covershot") or ""
                
                episodes[str(episode_number)] = Episode(str(episode_number), episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
            
            logging.info(f"Successfully extracted {len(episodes)} episodes")
        else:
            logging.error("Failed to find episode data in JSON")
        
    except Exception as e:
        logging.error(f"Failed to extract Prime Video data: {e}")
        return {}
    finally:
        if page:
            cleanup_playwright_page(page)
    
    return episodes