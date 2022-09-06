import logging
from ..common import Episode
from ..common import ini_webdriver
from selenium.webdriver.common.by import By
import re

# ex: https://www.amazon.co.jp/%E7%AC%AC02%E8%A9%B1/dp/B07TRLY369/
def primevideo_extractor(url):
    logging.info("primevideo_extractor is called")

    driver = ini_webdriver(headless=False)
    driver.get(url)
    try:
        epExpander = driver.find_element(By.CSS_SELECTOR, value="a[data-automation-id='ep-expander']")
        # epExpander = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.CSS_SELECTOR, value="a[data-automation-id='ep-expander']"))
        driver.get(epExpander.get_attribute("href"))
    except:
        pass

    # episodes = WebDriverWait(driver, timeout=60).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="li[id*='av-ep-episodes-']"))
    episodes = {}
    episodeNumber = 1
    for episode in driver.find_elements(By.CSS_SELECTOR, value="li[id*='av-ep-episodes-']"):
        episode_number = episodeNumber
        episode_name = episode.find_elements(By.CSS_SELECTOR, value="span[dir='auto']")[0].text.split(' ', 1)[1]
        if episode_name.__contains__('「') and episode_name.endswith('」') :
            episode_name = re.search(r'「(.*?)」', episode_name).group(1)
        if episode_name.__contains__('｢') and episode_name.endswith('｣') :
            episode_name = re.search(r'｢(.*?)｣', episode_name).group(1)
        episode_name = episode_name.lstrip(f"第{episode_number}話 ").lstrip("　").lstrip(f"#{episode_number} ")
        episode_air_date = re.findall(r'<div>(.*?)</div>', episode.get_attribute('innerHTML'))[0]
        if episode_air_date.__contains__('年'):
            episode_air_date = episode_air_date.replace('年', '-').replace('月', '-').replace('日', '')
        episode_runtime = re.findall(r'<div>(.*?)</div>', episode.get_attribute('innerHTML'))[1]
        from ..common import convert_runtime
        episode_runtime = convert_runtime(episode_runtime)
        episode_overview = episode.find_element(By.CSS_SELECTOR, value="div[data-automation-id*='synopsis'] div[dir='auto']").get_attribute('innerText').split('(C)', 1)[0].split('(Ｃ)', 1)[0].split('(ｃ)', 1)[0]
        episode_backdrop = re.search(r'src=\"(.*?)\"', episode.find_element(By.CSS_SELECTOR, value="noscript").get_attribute('innerText')).group(1)
        
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episodeNumber = episodeNumber + 1

    driver.close()
    return episodes