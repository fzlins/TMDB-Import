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

def create_csv(filename, import_data = {}):
    encoding = config.get("DEFAULT","encoding", fallback="utf-8-sig")
    import_data = remove_duplicate_overview(import_data)
    import_data = remove_duplicate_backdrop(import_data)
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

def ini_webdriver(headless=True, save_user_profile = False, images = False):
    from selenium import webdriver
    browser = config.get("DEFAULT","browser", fallback="edge")
    save_user_profile = config.getboolean("DEFAULT","save_user_profile", fallback=save_user_profile)
    if browser.lower() == "chrome":
        options = webdriver.ChromeOptions()
    else:
        options = webdriver.EdgeOptions()

    if headless:
        options.add_argument('--headless')
    if save_user_profile:
        user_date_dir = os.path.join(os.getcwd(), "Selenium")
        options.add_argument("user-data-dir=" + user_date_dir)
    options.add_argument('--disable-gpu')
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_argument("--disable-blink-features=AutomationControlled")
    if images:
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 1})
    else:
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

    if browser.lower() == "chrome":
        driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Edge(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def open_url(url, encoding = ""):
    if encoding == "":
        encoding = config.get("DEFAULT","encoding", fallback="utf-8-sig")
    from urllib.request import Request, urlopen
    req = Request(url)
    userAgernt = "Mozilla/5.0 (Windows NT 6.3;Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
    req.add_header('User-Agent', userAgernt)
    return urlopen(req, timeout=30).read().decode(encoding, "ignore")
