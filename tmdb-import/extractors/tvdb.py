import logging
from ..common import Episode
from ..common import ini_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime

# Ex: https://thetvdb.com/series/fourwheeler/seasons/official/1
def tvdb_extractor(url):
    logging.info("tvdb_extractor is called")

    driver = ini_webdriver(headless=False, save_user_profile=True)
    driver.get(url)
    
    episodes = {}
    for episode in WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="table[class='table table-bordered'] tbody tr")):
        all_columns = episode.find_elements(By.TAG_NAME,"td")
        episode_number = int(all_columns[0].text.rsplit('E', 1)[-1])
        episode_name = all_columns[1].find_element(By.TAG_NAME, value="a").text
        air_date = all_columns[2].find_element(By.TAG_NAME, value="div").text.strip()
        if air_date != "":
            episode_air_date = datetime.strptime(air_date, "%B %d, %Y").date()
        else:
            episode_air_date = ""
        episode_runtime = all_columns[3].text
        episode_overview = ""
        episode_backdrop = ""
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
    
    driver.close()
    return episodes