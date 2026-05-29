from .common import *
import logging

def extract_from_url(url, language="zh-CN"):
    from urllib.parse import urlparse
    urlData = urlparse(url)
    domain = urlData.netloc
    
    metadata = None
    if domain.endswith("anidb.net"):
        from .extractors import anidb
        metadata = anidb.anidb_extractor(url)
    elif domain.endswith("tv-asahi.co.jp"):
        from .extractors import asahi
        metadata = asahi.asahi_extractor(url)
    elif domain.endswith("tv.apple.com"):
        from .extractors import apple
        metadata = apple.apple_extractor(url)
    elif domain.endswith(".bilibili.com"):
        from .extractors import bilibili
        metadata = bilibili.bilibili_extractor(url)
    elif domain.endswith(".bilibili.tv"):
        from .extractors import biliintl
        metadata = biliintl.bilibili_tv_extractor(url)
    elif domain.endswith(".crunchyroll.com"):
        from .extractors import crunchyroll
        metadata = crunchyroll.crunchyroll_extractor(url)
    elif domain.endswith(".cctv.com"):
        from .extractors import cctv
        metadata = cctv.cctv_extractor(url)
    elif domain.endswith(".hbomax.com"):
        from .extractors import hbomax
        metadata = hbomax.hbomax_extractor(url=url)
    elif domain.endswith(".tvbanywhere.com"):
        from .extractors import tvbanywhere
        metadata = tvbanywhere.tvbanywhere_extractor(url=url)
    elif domain.__contains__("fod.fujitv."):
        from .extractors import fod
        metadata = fod.fod_extractor(url)
    elif domain.endswith(".iqiyi.com"):
        from .extractors import iqiyi
        metadata = iqiyi.iqiyi_extractor(url)
    elif domain.endswith(".ixigua.com"):
        from .extractors import ixigua
        metadata = ixigua.ixigua_extractor(url)
    elif domain.endswith("kktv.me"):
        from .extractors import kktv
        metadata = kktv.kktv_extractor(url)
    elif domain.endswith(".ptsplus.tv"):
        from .extractors import ptsplus
        metadata = ptsplus.ptsplus_extractor(url)
    elif domain.endswith(".litv.tv"):
        from .extractors import litv
        metadata = litv.litv_extractor(url)
    elif domain.endswith(".linetv.tw"):
        from .extractors import linetv
        metadata = linetv.linetv_extractor(url)
    elif domain.endswith(".mgtv.com"):
        from .extractors import mgtv
        metadata = mgtv.mgtv_extractor(url)
    elif domain.endswith(".miguvideo.com"):
        from .extractors import migu
        metadata = migu.migu_extractor(url)
    elif domain.endswith("myvideo.net.tw"):
        from .extractors import myvideo
        metadata = myvideo.myvideo_extractor(url)
    elif domain.__contains__(".mytvsuper."):
        from .extractors import mytvsuper
        metadata = mytvsuper.mytvsuper_extractor(url)
    elif url.__contains__(".netflix."):
        from .extractors import netflix
        metadata = netflix.netflix_extractor(url)
    elif domain.endswith(".nhk.jp") or domain.endswith(".nhk.or.jp"):
        from .extractors import nhk
        metadata = nhk.nhk_extractor(url)
    elif domain.endswith("tver.jp"):
        from .extractors import tver
        metadata = tver.tver_extractor(url)
    elif domain.endswith(".paravi.jp"):
        from .extractors import paravi
        metadata = paravi.paravi_extractor(url)
    elif domain.__contains__(".amazon.") or domain.__contains__(".primevideo."):
        from .extractors import primevideo
        metadata = primevideo.primevideo_extractor(url)
    elif domain.endswith(".qq.com"):
        from .extractors import qq
        metadata = qq.qq_extractor(url)
    elif domain.endswith(".sohu.com"):
        from .extractors import sohu
        metadata = sohu.sohu_extractor(url)
    elif domain.endswith("thetvdb.com"):
        from .extractors import tvdb
        metadata = tvdb.tvdb_extractor(url)
    elif domain.endswith(".viki.com"):
        from .extractors import viki
        metadata = viki.viki_extractor(url)
    elif domain.endswith(".viu.com"):
        from .extractors import viu
        metadata = viu.viu_extractor(url)
    elif domain.endswith(".wavve.com"):
        from .extractors import wavve
        metadata = wavve.wavve_extractor(url)
    elif domain.__contains__(".yahoo."):
        from .extractors import yahoo
        metadata = yahoo.yahoo_extractor(url)
    elif domain.endswith(".youku.com"):
        from .extractors import youku
        metadata = youku.youku_extractor(url)
    elif domain.endswith(".youtube.com") or domain.endswith("youtu.be"):
        from .extractors import youtube
        metadata = youtube.youtube_extractor(url)
    else:
        logging.info(f"Do not support {domain}")
        return

    if metadata:
        chinese_target = config.get("DEFAULT", "chinese_convert", fallback="").strip()
        if chinese_target:
            from .util.chinese_convert import is_chinese_language, convert_metadata
            if is_chinese_language(metadata.language):
                logging.info(f"Converting Chinese text to {chinese_target}")
                convert_metadata(metadata, chinese_target)

        # Process episodes in metadata: remove duplicates and apply filters
        from .common import process_episodes
        for season in metadata.seasons:
            if isinstance(season.episodes, dict) and season.episodes:
                season.episodes = process_episodes(season.episodes)

    logging.info(f"Extracting data is complete")
    return metadata
