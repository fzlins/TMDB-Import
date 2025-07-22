import logging
from ..common import Episode
from ..common import ini_playwright_page, cleanup_playwright_page

# Ex: https://anidb.net/anime/2073
def anidb_extractor(url):
    logging.info("anidb_extractor is called")

    page = ini_playwright_page(headless=False, save_user_profile=True)
    
    try:
        page.goto(url)
        
        episodes = {}
        episode_number = 1
        
        # Wait for episode elements to be present and get all episodes
        page.wait_for_selector("tr[itemprop='episode']", timeout=30000)
        episode_elements = page.locator("tr[itemprop='episode']").all()
        
        for episode in episode_elements:
            all_columns = episode.locator("td").all()
            number = all_columns[1].text_content().strip()
            if number.isnumeric():
                while episode_number <= int(number):
                    if int(number) == episode_number:
                        episode_name = all_columns[2].locator("label[itemprop='name']").text_content()
                        episode_air_date = all_columns[4].get_attribute('content')
                        episode_runtime = all_columns[3].text_content()
                        episode_overview = ""
                        episode_backdrop = ""
                        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
                    else:
                        episode_name = ""
                        episode_air_date = "null"
                        episode_runtime = all_columns[3].text_content()
                        episode_overview = ""
                        episode_backdrop = ""
                        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
                        
                    episode_number = episode_number + 1

                # try:
                    # en
                    # summary = all_columns[2].locator("span[class='i_icon i_summary']").get_attribute('title')
                # except:
                    # pass

        return episodes
    
    finally:
        cleanup_playwright_page(page)