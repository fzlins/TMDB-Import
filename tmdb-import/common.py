import configparser
import os
import re
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8-sig')

class Person:
    def __init__(self, *args):
        self.id = None
        self.name = None
        self.overview = None

class Episode:
    def __init__(self, episode_number, name="", air_date ="null", runtime = "", overview="", backdrop=""):
        self.episode_number = episode_number
        self.name = name
        self.air_date = air_date
        self.runtime = runtime
        self.overview = overview
        self.backdrop = backdrop
        self.csv_header = ["episode_number", "name", "air_date", "runtime", "overview", "backdrop"]

    def __iter__(self):
        return iter([self.episode_number, self.name, self.air_date, self.runtime, self.overview, self.backdrop])

class Season():
    def __init__(self, season_number, name="", overview="", episodes={}, poster="", crew={}, guest_stars={}):
        self.season_number = season_number
        self.name = name
        self.overview = overview
        self.episodes = episodes
        self.poster = poster
        self.crew = crew
        self.guest_stars = guest_stars

class TV():
    def __init__(self, *args):
        self.id = None
        self.name = None
        self.overview = None
        self.poster = None

def remove_duplicate_overview(import_data):
    overview_dict = {}
    for value in import_data.values():
        if value.overview != "":
            if (value.overview in overview_dict.keys()):
                overview_dict[value.overview] = overview_dict[value.overview] + 1
            else:
                overview_dict[value.overview] = 1
                
    for value in import_data.values():
        if value.overview != "" and overview_dict[value.overview] > 1:
            import_data[value.episode_number].overview = ""
        
    return import_data

def remove_duplicate_backdrop(import_data):
    backdrop_dict = {}
    for value in import_data.values():
        if value.backdrop != "":
            if (value.backdrop in backdrop_dict.keys()):
                backdrop_dict[value.backdrop] = backdrop_dict[value.backdrop] + 1
            else:
                backdrop_dict[value.backdrop] = 1
                
    for value in import_data.values():
        if value.backdrop != "" and backdrop_dict[value.backdrop] > 1:
            import_data[value.episode_number].backdrop = ""
        
    return import_data

def filter_by_name(import_data, filter_words):
    if not filter_words:
        return import_data
    
    filtered_data = {}
    filter_list = [word.strip() for word in filter_words.split(',')]
    
    for episode_number, episode in import_data.items():
        should_keep = True
        if not episode.name:
            filtered_data[episode_number] = episode
            continue

        for word in filter_list:
            if word and word in episode.name:
                should_keep = False
                break
        if should_keep:
            filtered_data[episode_number] = episode

    return filtered_data

def create_csv(filename, import_data = {}):
    encoding = config.get("DEFAULT","encoding", fallback="utf-8-sig")
    filter_words = config.get("DEFAULT", "filter_words", fallback="")
    import_data = remove_duplicate_overview(import_data)
    import_data = remove_duplicate_backdrop(import_data)
    import_data = filter_by_name(import_data, filter_words)
    
    # Renumber episodes sequentially
    renumbered_data = {}
    episode_count = 1
    for original_episode_number, episode in import_data.items():
        episode.episode_number = str(episode_count)
        renumbered_data[episode.episode_number] = episode
        episode_count += 1
    import_data = renumbered_data

    import csv
    with open(filename, "w", newline='', encoding=encoding) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(import_data.values())[0].csv_header)
        writer.writerows(list(import_data.values()))
        csvfile.close()

def read_csv(filename):
    encoding = config.get("DEFAULT","encoding", fallback="utf-8-sig")
    importData = {}
    import csv
    with open(filename, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            importData[row['episode_number'].strip()] = row
        csvfile.close()
    return importData

def ini_playwright_page(headless=True, save_user_profile=False, images=False):
    """
    Initialize a Playwright browser page with Chrome/Chromium.
    
    Args:
        headless (bool): Run browser in headless mode
        save_user_profile (bool): Use persistent browser context with user data
        images (bool): Enable/disable image loading
    
    Returns:
        playwright.sync_api.Page: Playwright page object
    """
    from playwright.sync_api import sync_playwright
    
    # Get configuration values
    save_user_profile = config.getboolean("DEFAULT", "save_user_profile", fallback=save_user_profile)
    
    # Initialize Playwright
    playwright = sync_playwright().start()
    
    # Common launch arguments
    common_args = [
        '--disable-gpu',
        '--autoplay-policy=no-user-gesture-required',
        '--disable-blink-features=AutomationControlled',
        '--no-first-run',
        '--disable-default-apps'
    ]
    
    # Create browser context
    if save_user_profile:
        user_data_dir = os.path.join(os.getcwd(), "Browser")
        # Create directory if it doesn't exist
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Launch with persistent context
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            args=common_args,
            timeout=60000  # Increase timeout for persistent context
        )
        browser = None  # No separate browser object when using persistent context
    else:
        # Launch regular browser
        browser = playwright.chromium.launch(
            headless=headless,
            args=common_args
        )
        context = browser.new_context()
    
    # Block images if requested
    if not images:
        context.route("**/*.{png,jpg,jpeg,gif,webp,svg,ico}", lambda route: route.abort())
    
    # Create new page
    page = context.new_page()
    
    # Hide webdriver property to avoid detection
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Store references for cleanup
    page._playwright_context = context
    page._playwright_browser = browser
    page._playwright_instance = playwright
    page._is_persistent = save_user_profile
    
    return page

def cleanup_playwright_page(page):
    """
    Properly cleanup Playwright page, context, browser and instance.
    
    Args:
        page: Playwright page object with attached cleanup references
    """
    try:
        # Close page first
        if hasattr(page, 'close') and not page.is_closed():
            page.close()
            
        # Close context
        if hasattr(page, '_playwright_context') and page._playwright_context:
            page._playwright_context.close()
            
        # Close browser (only if not using persistent context)
        if hasattr(page, '_playwright_browser') and page._playwright_browser:
            if not getattr(page, '_is_persistent', False):
                page._playwright_browser.close()
                
        # Stop Playwright instance
        if hasattr(page, '_playwright_instance') and page._playwright_instance:
            page._playwright_instance.stop()
            
    except Exception as e:
        print(f"Warning: Error during Playwright cleanup: {e}")



def open_url(url, encoding = ""):
    if encoding == "":
        encoding = config.get("DEFAULT","encoding", fallback="utf-8-sig")
    from urllib.request import Request, urlopen
    req = Request(url)
    userAgernt = "Mozilla/5.0 (Windows NT 6.3;Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
    req.add_header('User-Agent', userAgernt)
    return urlopen(req, timeout=30).read().decode(encoding, "ignore")
