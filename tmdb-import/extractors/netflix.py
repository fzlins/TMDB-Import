import logging
import re
from ..common import Episode
from ..common import ini_webdriver
from selenium.webdriver.common.by import By

# ex: https://webcache.googleusercontent.com/search?q=cache:lPwlbfO5SXQJ:https://www.netflix.com/sg-zh/title/81568217&cd=1&hl=zh-CN&ct=clnk&gl=ca
def netflix_extractor(url):
    logging.info("netflix_extractor is called")

    driver = ini_webdriver()
    driver.get(url)
    source_data = driver.find_elements(By.CLASS_NAME, value="episode")
    episodes = {}
    episode_number = 1
    for episode in source_data:
        episode_number = episode_number
        episode_name = episode.find_element(By.CLASS_NAME, value="episode-title").text
        episode_name = re.split('\.|。', episode_name, maxsplit=1)[1]
        episode_air_date = ""
        episode_runtime = ''.join(filter(str.isdigit, episode.find_element(By.CLASS_NAME, value="episode-runtime").text))
        episode_overview = episode.find_element(By.CLASS_NAME, value="epsiode-synopsis").get_attribute('innerText')
        episode_backdrop = ""
        
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episode_number = episode_number + 1

    driver.close()
    return episodes