import logging
from ..common import Episode
from ..common import ini_playwright_page, cleanup_playwright_page
from datetime import datetime

# Ex: https://thetvdb.com/series/fourwheeler/seasons/official/1
def tvdb_extractor(url):
    logging.info("tvdb_extractor is called")

    page = ini_playwright_page(headless=False, save_user_profile=True)
    
    try:
        page.goto(url)
        
        # Wait for the table to be present and get all episode rows
        page.wait_for_selector("table.table.table-bordered tbody tr", timeout=30000)
        episode_rows = page.locator("table.table.table-bordered tbody tr").all()
        
        episodes = {}
        for episode_row in episode_rows:
            all_columns = episode_row.locator("td").all()
            
            # Extract episode number from first column (format: "S1E1" -> extract "1")
            episode_number = int(all_columns[0].text_content().rsplit('E', 1)[-1])
            
            # Extract episode name from link in second column
            episode_name = all_columns[1].locator("a").text_content()
            
            # Extract air date from div in third column
            air_date = all_columns[2].locator("div").text_content().strip()
            if air_date != "":
                episode_air_date = datetime.strptime(air_date, "%B %d, %Y").date()
            else:
                episode_air_date = ""
            
            # Extract runtime from fourth column
            episode_runtime = all_columns[3].text_content()
            
            episode_overview = ""
            episode_backdrop = ""
            episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        
        return episodes
        
    finally:
        cleanup_playwright_page(page)