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
        source_data = page.locator("li[data-uia='episode-card']").all()
        episodes = {}
        episode_number = 1
        for episode in source_data:
            episode_number = episode_number
            episode_name = episode.locator("p[data-uia='episode-title']").text_content()
            episode_name = re.split(r'\.|。', episode_name, maxsplit=1)[1].strip()
            episode_air_date = ""
            runtime_text = episode.locator("div:first-child span").last.text_content()
            runtime_parts = re.findall(r'\d+', runtime_text)
            if len(runtime_parts) >= 2:
                episode_runtime = str(int(runtime_parts[0]) * 60 + int(runtime_parts[1]))
            elif len(runtime_parts) == 1:
                episode_runtime = runtime_parts[0]
            else:
                episode_runtime = ""
            episode_overview = episode.locator("p:not([data-uia='episode-title'])").text_content()
            episode_backdrop = ""
            
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
            episode_number = episode_number + 1
    finally:
        cleanup_playwright_page(page)
    
    return episodes