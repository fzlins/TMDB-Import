import json
import logging
from ..common import Episode
from ..common import ini_playwright_page, cleanup_playwright_page
import re

# ex: https://www.myvideo.net.tw/details/3/11347#
def myvideo_extractor(url):
    logging.info("myvideo_extractor is called")

    page = ini_playwright_page()
    page.goto(url)

    try:
        season_name = page.locator("div[class='title'] h2").text_content()
        logging.info(f"name: {season_name}")
        season_overview = page.locator("p[class='describe']").text_content()
        logging.info(f"overview: {season_overview}")
        #season_poster = get_large_image(season_poster)
        #logging.info(f"poster: {season_poster}")
        season_backdrops = page.locator("figure[class='movieStillsItem'] picture img").all()
        for backdrop in season_backdrops:
            season_backdrop = get_large_image(backdrop.get_attribute("src"))
            logging.info(f"backdrop: {season_backdrop}")
    except Exception as e:
        logging.warning(f"Could not extract season-level information: {e}")

    source_data = page.locator("figure[class='episodeItemArea movieItemArea ']").all()
    episodes = {}
    episode_number = 1
    logging.info(f"source_data: {len(source_data)}")
    for episode in source_data:
        videoTitle = episode.locator("span[class='episodeIntro movieIntro'] a")
        episode_url = videoTitle.get_attribute('href')

        title = videoTitle.text_content()
        if not title.__contains__(f'第{episode_number}集'):
            continue

        episode_number = episode_number
        episode_name = ""
        if title.__contains__('【'):
            episode_name = re.search(r'【(.*?)】', title).group(1)
        episode_air_date = ""
        episode_runtime = ""
        episode_overview_element = episode.locator("span[class='episodeIntro movieIntro'] blockquote")
        episode_overview = episode_overview_element.text_content() if episode_overview_element.count() > 0 else ""
        episode_backdrop = episode.locator("img[class='episodePhoto moviePhoto']").get_attribute('src')
        episode_backdrop = get_large_image(episode_backdrop)
        
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episode_number = episode_number + 1

    cleanup_playwright_page(page)
    return episodes

def get_large_image(url):
    return url.split('_', 1)[0] + '.' + url.rsplit('.', 1)[-1]