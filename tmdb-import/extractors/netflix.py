import logging
import re
from ..common import Episode
from ..common import ini_playwright_page, cleanup_playwright_page

# ex: https://webcache.googleusercontent.com/search?q=cache:lPwlbfO5SXQJ:https://www.netflix.com/sg-zh/title/81568217&cd=1&hl=zh-CN&ct=clnk&gl=ca
def netflix_extractor(url):
    logging.info("netflix_extractor is called")

    page = ini_playwright_page()
    try:
        page.goto(url)
        source_data = page.locator(".episode").all()
        episodes = {}
        episode_number = 1
        for episode in source_data:
            episode_number = episode_number
            episode_name = episode.locator(".episode-title").text_content()
            episode_name = re.split('\.|。', episode_name, maxsplit=1)[1]
            episode_air_date = ""
            episode_runtime = ''.join(filter(str.isdigit, episode.locator(".episode-runtime").text_content()))
            episode_overview = episode.locator(".epsiode-synopsis").get_attribute('innerText')
            episode_backdrop = ""
            
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
            episode_number = episode_number + 1
    finally:
        cleanup_playwright_page(page)
    
    return episodes