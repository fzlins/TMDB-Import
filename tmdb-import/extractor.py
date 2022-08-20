
class MoiveExtractor():
    def __init__(self, *args):
        self.url = None
        self.title = None
        self.vid = None

        if args:
            self.url = args[0]

class SeriesExtractor():
    def __init__(self, *args):
        self.url = None
        self.title = None
        self.vid = None

        if args:
            self.url = args[0]