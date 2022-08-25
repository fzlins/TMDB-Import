import logging
from ..common import Episode
from ..common import ini_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# Ex: https://anidb.net/anime/2073
def anidb_extractor(url):
    logging.info("anidb_extractor is called")

    driver = ini_webdriver(headless=False, save_user_profile=True)
    driver.get(url)
    
    episodes = {}
    for episode in WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="tr[itemprop='episode']")):
        all_columns = episode.find_elements(By.TAG_NAME,"td")
        episode_number = all_columns[1].text.strip()
        if episode_number.isnumeric():
            episode_name = all_columns[2].find_element(By.CSS_SELECTOR, value="label[itemprop='name']").text
            episode_air_date = all_columns[4].get_attribute('content')
            episode_runtime = all_columns[3].text
            episode_overview = ""
            episode_backdrop = ""
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
            
            # try:
                # en
                # summary = all_columns[2].find_element(By.CSS_SELECTOR, value="span[class='i_icon i_summary']").get_attribute('title')
            # except:
                # pass

    return episodes