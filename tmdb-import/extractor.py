from .common import *

def extract_from_url(url):
    episodes = {}
    if url.__contains__(".bilibili.com/"):
        from .extractors import bilibili
        episodes = bilibili.bilibili_extractor(url)
    elif url.__contains__(".disneyplus.com/"):
        from .extractors import disneyplus
        episodes = disneyplus.disneyplus_extractor(url)
    elif url.__contains__(".iqiyi.com/"):
        from .extractors import iqiyi
        episodes = iqiyi.iqiyi_extractor(url)
    elif url.__contains__(".mgtv.com/"):
        from .extractors import mgtv
        episodes = mgtv.mgtv_extractor(url)
    elif url.__contains__(".qq.com/"):
        from .extractors import qq
        episodes = qq.qq_extractor(url)
    elif url.__contains__(".wavve.com/"):
        from .extractors import wavve
        episodes = wavve.wavve_extractor(url)
    elif url.__contains__("youku.com"):
        from .extractors import youku
        episodes = youku.youku_extractor(url)

    if len(episodes) > 0:
        create_csv("import.csv", episodes)