from .common import *
from urllib.parse import urlparse

def extract_from_url(url):
    episodes = {}
    urlData = urlparse(url)
    domain = urlData.netloc
    if domain.endswith("disneyplus.com"):
        from .extractors import disneyplus
        episodes = disneyplus.disneyplus_extractor(url)
    elif domain.endswith("iqiyi.com"):
        from .extractors import iqiyi
        episodes = iqiyi.iqiyi_extractor(url)
    elif domain.endswith("mgtv.com"):
        from .extractors import mgtv
        episodes = mgtv.mgtv_extractor(url)
    elif domain.endswith(".wavve.com"):
        from .extractors import wavve
        episodes = wavve.wavve_extractor(url)

    if len(episodes) > 0:
        create_csv("import.csv", episodes)