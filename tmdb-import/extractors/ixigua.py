import logging
import re
from selenium.webdriver.common.by import By
from ..common import Episode
from ..common import ini_webdriver
from selenium.webdriver.support.ui import WebDriverWait

# ixigua ex: https://www.ixigua.com/7144949347581428232
def ixigua_extractor(url):
    logging.info("ixigua_extractor is called")

    driver = ini_webdriver(headless= False)
    driver.get(url)
    
    WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, value="ProgramGuide__title-span"))
    season_name = driver.find_element(By.CLASS_NAME, value="ProgramGuide__title-span").text
    logging.info(f"name: {season_name}")
    WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CSS_SELECTOR, value="meta[name='description']"))
    season_overview = driver.find_element(By.CSS_SELECTOR, value="meta[name='description']").text
    logging.info(f"overview: {season_overview}")

    source_data = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="div[class*='richPlayCard dark']"))
    episode_number = 1
    episodes = {}
    for episode in source_data:
        episode_number = episode_number
        episode_name = episode.find_element(By.CSS_SELECTOR, value="div[class='title']").text

        episode_air_date = ""
        episode_runtime = ""
        episode_overview = ""
        episode_backdrop = episode.find_element(By.TAG_NAME, value="img").get_attribute('src')
        
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episode_number = episode_number + 1
    driver.close()
    return episodes