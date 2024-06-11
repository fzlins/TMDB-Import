from .common import *
import logging

def extract_from_url(url, language="zh-CN"):
    from urllib.parse import urlparse
    urlData = urlparse(url)
    domain = urlData.netloc
    
    episodes = {}
    if domain.endswith("anidb.net"):
        from .extractors import anidb
        episodes = anidb.anidb_extractor(url)
    elif domain.endswith("tv-asahi.co.jp"):
        from .extractors import asahi
        episodes = asahi.asahi_extractor(url)
    elif domain.endswith("tv.apple.com"):
        from .extractors import apple
        episodes = apple.apple_extractor(url)
    elif domain.endswith(".bilibili.com"):
        from .extractors import bilibili
        episodes = bilibili.bilibili_extractor(url)
    elif domain.endswith(".cctv.com"):
        from .extractors import cctv
        episodes = cctv.cctv_extractor(url)
    elif domain.endswith(".disneyplus.com"):
        from .extractors import disneyplus
        episodes = disneyplus.disneyplus_extractor(url=url, language=language)
    elif domain.__contains__("fod.fujitv."):
        from .extractors import fod
        episodes = fod.fod_extractor(url)
    elif domain.endswith(".iqiyi.com"):
        from .extractors import iqiyi
        episodes = iqiyi.iqiyi_extractor(url)
    elif domain.endswith(".ixigua.com"):
        from .extractors import ixigua
        episodes = ixigua.ixigua_extractor(url)
    elif domain.endswith("kktv.me"):
        from .extractors import kktv
        episodes = kktv.kktv_extractor(url)
    elif domain.endswith(".mgtv.com"):
        from .extractors import mgtv
        episodes = mgtv.mgtv_extractor(url)
    elif domain.endswith("myvideo.net.tw"):
        from .extractors import myvideo
        episodes = myvideo.myvideo_extractor(url)
    elif domain.__contains__(".mytvsuper."):
        from .extractors import mytvsuper
        episodes = mytvsuper.mytvsuper_extractor(url)
    elif url.__contains__(".netflix."):
        from .extractors import netflix
        episodes = netflix.netflix_extractor(url)
    elif domain.endswith(".nhk.jp") or domain.endswith(".nhk.or.jp"):
        from .extractors import nhk
        episodes = nhk.nhk_extractor(url)
    elif domain.endswith(".paravi.jp"):
        from .extractors import paravi
        episodes = paravi.paravi_extractor(url)
    elif domain.__contains__(".amazon.") or domain.__contains__(".primevideo."):
        from .extractors import primevideo
        episodes = primevideo.primevideo_extractor(url)
    elif domain.endswith(".qq.com"):
        from .extractors import qq
        episodes = qq.qq_extractor(url)
    elif domain.endswith(".sohu.com"):
        from .extractors import sohu
        episodes = sohu.sohu_extractor(url)
    elif domain.endswith("thetvdb.com"):
        from .extractors import tvdb
        episodes = tvdb.tvdb_extractor(url)
    elif domain.endswith(".viki.com"):
        from .extractors import viki
        episodes = viki.viki_extractor(url)
    elif domain.endswith(".viu.com"):
        from .extractors import viu
        episodes = viu.viu_extractor(url)
    elif domain.endswith(".wavve.com"):
        from .extractors import wavve
        episodes = wavve.wavve_extractor(url)
    elif domain.__contains__(".yahoo."):
        from .extractors import yahoo
        episodes = yahoo.yahoo_extractor(url)
    elif domain.endswith(".youku.com"):
        from .extractors import youku
        episodes = youku.youku_extractor(url)
    else:
        logging.info(f"Do not support {domain}")
        return

    if len(episodes) > 0:
        create_csv("import.csv", episodes)

    logging.info(f"Extracting data is complete")