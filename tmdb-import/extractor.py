from .common import *
import logging

def extract_from_url(url, language="zh-CN"):
    episodes = {}
    if url.__contains__(".bilibili.com/"):
        from .extractors import bilibili
        episodes = bilibili.bilibili_extractor(url)
    elif url.__contains__(".disneyplus.com/"):
        from .extractors import disneyplus
        episodes = disneyplus.disneyplus_extractor(url=url, language=language)
    elif url.__contains__(".iqiyi.com/"):
        from .extractors import iqiyi
        episodes = iqiyi.iqiyi_extractor(url)
    elif url.__contains__(".kktv.me/"):
        from .extractors import kktv
        episodes = kktv.kktv_extractor(url)
    elif url.__contains__(".mgtv.com/"):
        from .extractors import mgtv
        episodes = mgtv.mgtv_extractor(url)
    elif url.__contains__(".paravi.jp/"):
        from .extractors import paravi
        episodes = paravi.paravi_extractor(url)
    elif url.__contains__(".qq.com/"):
        from .extractors import qq
        episodes = qq.qq_extractor(url)
    elif url.__contains__(".viki.com/"):
        from .extractors import viki
        episodes = viki.viki_extractor(url)
    elif url.__contains__(".viu.com/"):
        from .extractors import viu
        episodes = viu.viu_extractor(url)
    elif url.__contains__(".wavve.com/"):
        from .extractors import wavve
        episodes = wavve.wavve_extractor(url)
    elif url.__contains__("youku.com"):
        from .extractors import youku
        episodes = youku.youku_extractor(url)

    if len(episodes) > 0:
        create_csv("import.csv", episodes)

    logging.info(f"Extracting data is complete")