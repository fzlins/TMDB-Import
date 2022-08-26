import logging
import re
import time
from selenium.webdriver.common.by import By
from ..common import Episode
from ..common import ini_webdriver
from selenium.webdriver.support.ui import WebDriverWait

# paravi ex: https://www.paravi.jp/title/64465
def paravi_extractor(url):
    logging.info("paravi_extractor is called")

    driver = ini_webdriver()
    driver.get(url)
    WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CSS_SELECTOR, value="i[class='fa-angle_down']")).click()
    source_data = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="div[class='card episode-card']"))
    episode_number = 1
    episodes = {}
    for episode in source_data:
        episode_number = episode_number
        episode_name = episode.find_element(By.CSS_SELECTOR, value="h2[class='title'] p").text.lstrip(f"#{episode_number} ")
        if episode_name.__contains__("episode"):
            episode_name = ""
        episode_air_date = ""
        episode_runtime = episode.find_element(By.CSS_SELECTOR, value="span[class='duration']").text
        episode_overview = episode.find_element(By.CSS_SELECTOR, value="div[class='synopsis']").text
        episode_backdrop = episode.find_element(By.CSS_SELECTOR, value="div[class='artwork']").get_attribute('style')
        episode_backdrop = re.search(r'url\(\"(.*?)\?', episode_backdrop).group(1)
        
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episode_number = episode_number + 1
    driver.close()
    return episodes