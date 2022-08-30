import logging
from ..common import Episode
from ..common import ini_webdriver
from selenium.webdriver.common.by import By
import re

# ex: https://www.myvideo.net.tw/details/3/11347#
def myvideo_extractor(url):
    logging.info("myvideo_extractor is called")

    driver = ini_webdriver()
    driver.get(url)

    season_name = driver.find_element(By.CSS_SELECTOR, value="div[class='title'] h1").text
    logging.info(f"name: {season_name}")
    season_overview = driver.find_element(By.CSS_SELECTOR, value="p[id='discriptMultiLine3']").text
    logging.info(f"overview: {season_overview}")
    season_poster = driver.find_element(By.CSS_SELECTOR, value="section[class='photoArea'] img").get_attribute("src")
    season_poster = get_large_image(season_poster)
    logging.info(f"poster: {season_poster}")
    season_backdrops = driver.find_elements(By.CSS_SELECTOR, value="ul[class='tabVideoList photoList tabList'] li img")
    for backdrop in season_backdrops:
        season_backdrop = get_large_image(backdrop.get_attribute("src"))
        logging.info(f"backdrop: {season_backdrop}")

    source_data = driver.find_elements(By.CSS_SELECTOR, value="ul[class='tabVideoList tabList'] li")
    episodes = {}
    episode_number = 1
    for episode in source_data:
        videoTitle = episode.find_element(By.CLASS_NAME, value="videoTitle")
        episode_url = videoTitle.get_attribute('href')
        title = videoTitle.text
        episode_number = episode_number
        episode_name = ""
        if title.__contains__('【'):
            episode_name = re.search(r'【(.*?)】', title).group(1)
        episode_air_date = ""
        episode_runtime = ""
        episode_overview = ""
        episode_backdrop = episode.find_element(By.CLASS_NAME, value="photo").get_attribute('src')
        episode_backdrop = get_large_image(episode_backdrop)
        
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episode_number = episode_number + 1

    driver.close()
    return episodes

def get_large_image(url):
    return url.split('_', 1)[0] + ".jpg"