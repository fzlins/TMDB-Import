import logging
import re
from ..common import Episode
from ..common import ini_playwright_page, cleanup_playwright_page

# paravi ex: https://www.paravi.jp/title/64465
def paravi_extractor(url):
    logging.info("paravi_extractor is called")

    page = ini_playwright_page()
    try:
        page.goto(url)
        
        season_name = page.locator(".active").text_content()
        logging.info(f"name: {season_name}")
        season_overview = page.locator(".synopsis").text_content()
        logging.info(f"overview: {season_overview}")
        season_backdrops = page.locator(".artwork")
        season_backdrop_style = season_backdrops.first.get_attribute('style')
        season_backdrop = re.search(r'url\(\"(.*?)\?', season_backdrop_style).group(1)
        logging.info(f"backdrop: {season_backdrop}")

        # Wait for and click the dropdown button
        page.locator("i[class='fa-angle_down']").click()
        
        # Wait for episode cards to load
        page.wait_for_selector("div[class='card episode-card']", timeout=30000)
        source_data = page.locator("div[class='card episode-card']").all()
        
        episode_number = 1
        episodes = {}
        for episode in source_data:
            episode_number = episode_number
            episode_name = episode.locator("h2[class='title'] p").text_content().lstrip(f"#{episode_number} ")

            if episode_name.__contains__("episode"):
                episode_name = ""
            elif episode_name.__contains__("予告"):
                continue

            episode_air_date = ""
            episode_runtime = episode.locator("span[class='duration']").text_content()
            episode_overview = episode.locator("div[class='synopsis']").text_content()
            episode_backdrop_style = episode.locator("div[class='artwork']").get_attribute('style')
            episode_backdrop = re.search(r'url\(\"(.*?)\?', episode_backdrop_style).group(1)
            
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
            episode_number = episode_number + 1
            
        return episodes
    finally:
        cleanup_playwright_page(page)