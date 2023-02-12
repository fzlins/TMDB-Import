import logging
from ..common import Episode
from ..common import ini_webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
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
    for episode in driver.find_elements(By.CSS_SELECTOR, value="li[id*='av-ep-episodes-']"):
        episode_name = episode.find_elements(By.CSS_SELECTOR, value="span[dir='auto']")[0].text.strip()
        episode_number = episode_name.split('.', 1)[0]
        episode_name = episode_name.removeprefix(f"{episode_number}.").strip()
        if episode_name.__contains__('「') and episode_name.__contains__('」') :
            episode_name = episode_name.split('「', 1)[1].replace("」", "")
        elif episode_name.__contains__('｢') and episode_name.__contains__('｣') :
            episode_name = episode_name.split('｢', 1)[1].replace("｣", "")
        elif episode_name.startswith('#'):
            episode_name = episode_name.removeprefix(f'#{episode_number}').lstrip()
        elif episode_name.startswith('第'):
            if episode_name.__contains__('話'):
                episode_name = episode_name.split('話', 1)[1].strip()
            elif episode_name.__contains__('回'):
                episode_name = episode_name.split('回', 1)[1].strip()

        episode_air_date = re.findall(r'<div>(.*?)</div>', episode.get_attribute('innerHTML'))[0]
        if episode_air_date.__contains__('年'):
            episode_air_date = episode_air_date.replace('年', '-').replace('月', '-').replace('日', '')
        
        try:
            episode_air_date = datetime.strptime(episode_air_date, '%B %d, %Y').date() + timedelta(days=1)
        except:
            pass

        episode_runtime = re.findall(r'<div>(.*?)</div>', episode.get_attribute('innerHTML'))[1]
        runtime = re.findall(r'\d+', episode_runtime)
        if len(runtime) > 1:
            episode_runtime = int(runtime[0])*60 + int(runtime[1])
        elif episode_runtime.__contains__("時間") or episode_runtime.__contains__("小时") or episode_runtime.__contains__("h"):
            episode_runtime = int(runtime[0])*60
        else:
            episode_runtime = int(runtime[0])

        episode_overview = episode.find_element(By.CSS_SELECTOR, value="div[data-automation-id*='synopsis'] div[dir='auto']").get_attribute('innerText')
        if episode_overview.__contains__("※"):
            episode_overview = episode_overview.rsplit('※', 1)[0]
        elif episode_overview.__contains__("©"):
            episode_overview = episode_overview.rsplit('©', 1)[0]

        episode_overview = re.split(r'[（\(][CＣｃc][）\)]', episode_overview, 1)[0]
        while episode_overview.__contains__('[') and episode_overview.endswith(']'):
            episode_overview = episode_overview.rsplit('[', 1)[0]

        episode_backdrop = re.search(r'src=\"(.*?)\"', episode.find_element(By.CSS_SELECTOR, value="noscript").get_attribute('innerText')).group(1)
        
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

    driver.close()
    return episodes