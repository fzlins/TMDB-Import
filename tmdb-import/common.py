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

def create_csv(filename, import_data = {}, encoding='utf-8-sig'):
    import csv
    with open(filename, "w", newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(import_data.values())[0].csv_header)
        writer.writerows(list(import_data.values()))

from selenium import webdriver
def ini_webdriver(headless=True, images = False):
    options = webdriver.EdgeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('log-level=3')
    if images:
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 1})
    else:
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

    driver = webdriver.Edge(options=options)
    return driver
