class Person:
    def __init__(self, *args):
        self.id = None
        self.name = None
        self.overview = None

class Episode:
    def __init__(self, episode_number, name, air_date, runtime, overview, backdrop):
        self.episode_number = episode_number
        self.name = name
        self.air_date = air_date
        self.runtime = runtime
        self.overview = overview
        self.backdrop = backdrop

class Season():
    def __init__(self, *args):
        self.season_number = None
        self.name = None
        self.overview = None
        self.episodes = {}
        self.poster = None
        self.crew = {}
        self.guest_stars = {}

class TV():
    def __init__(self, *args):
        self.id = None
        self.name = None
        self.overview = None
        self.poster = None