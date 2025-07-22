import logging
import re
from ..common import Episode
from ..common import ini_playwright_page, cleanup_playwright_page

# ixigua ex: https://www.ixigua.com/7144949347581428232
def ixigua_extractor(url):
    logging.info("ixigua_extractor is called")

    page = ini_playwright_page(headless=False)
    
    try:
        page.goto(url)
        
        # Wait for and extract season name
        page.wait_for_selector(".ProgramGuide__title-span", timeout=30000)
        season_name = page.locator(".ProgramGuide__title-span").text_content()
        logging.info(f"name: {season_name}")
        
        # Wait for and extract season overview from meta tag
        page.wait_for_selector("meta[name='description']", timeout=30000)
        season_overview = page.locator("meta[name='description']").get_attribute("content")
        logging.info(f"overview: {season_overview}")

        # Wait for and extract episode data
        page.wait_for_selector("div[class*='richPlayCard dark']", timeout=30000)
        source_data = page.locator("div[class*='richPlayCard dark']").all()
        
        episode_number = 1
        episodes = {}
        for episode in source_data:
            episode_name = episode.locator("div[class='title']").text_content()

            episode_air_date = ""
            episode_runtime = ""
            episode_overview = ""
            episode_backdrop = episode.locator("img").get_attribute('src')
            
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
            episode_number = episode_number + 1
            
    finally:
        cleanup_playwright_page(page)
        
    return episodes