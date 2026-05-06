import json
from urllib.parse import urlparse
import logging
from ..common import Episode, open_url
from datetime import datetime

# language: zh
# backdrop: 1920x1080
# Ex:"https://www.viu.com/ott/sg/zh/vod/2635502/

# 区域映射表
AREA_ID_MAP = {
    'sg': 2,    # 新加坡
    'hk': 1,    # 香港
    'th': 4,    # 泰国
    'ph': 5,    # 菲律宾
}

# 语言映射表
LANGUAGE_FLAG_ID_MAP = {
    'zh': 2,     # 简体中文
    'zh-cn': 2,  # 简体中文
    'zh-hk': 1,  # 繁体中文(香港)
    'en': 3,     # 英文
    'th': 4,     # 泰文
    'id': 8,     # 印度尼西亚文
}

def viu_extractor(url):
    logging.info("viu_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    # 解析 URL 路径: ott/{area}/{language}/vod/{product_id}
    path_parts = urlPath.split('/')
    if len(path_parts) >= 5:
        area_code = path_parts[1]  # sg
        language_code = path_parts[2]  # zh-cn
        product_id = path_parts[4]
    else:
        # 如果解析失败,使用默认值
        area_code = 'sg'
        language_code = 'zh-cn'
        product_id = urlPath.rsplit('/', 1)[-1]

    # 获取对应的 ID
    area_id = AREA_ID_MAP.get(area_code.lower(), 2)  # 默认值 2 (新加坡)
    language_flag_id = LANGUAGE_FLAG_ID_MAP.get(language_code.lower(), 2)  # 默认值 2 (简体中文)

    logging.debug(f"Parsed area_code: {area_code}, area_id: {area_id}")
    logging.debug(f"Parsed language_code: {language_code}, language_flag_id: {language_flag_id}")

    # 获取 series_id
    apiRequest = (f"https://api-gateway-global.viu.com/api/mobile?platform_flag_label=web&area_id={area_id}&language_flag_id={language_flag_id}&r=%2Fproduct%2Flistall&product_id={product_id}")
    logging.debug(f"API request url: {apiRequest}")
    resp = json.loads(open_url(apiRequest))
    products = resp.get('data', {}).get('product', [])
    match = next((p for p in products if str(p.get('product_id')) == str(product_id)), None)
    if not match:
        raise RuntimeError(f"Viu: 未找到 product_id={product_id} 的剧集信息。")
    series_id = match['series_id']

    # 获取剧集列表
    apiRequest = (f"https://api-gateway-global.viu.com/api/mobile?platform_flag_label=web&area_id={area_id}&language_flag_id={language_flag_id}&r=%2Fvod%2Fproduct-list&series_id={series_id}&size=1000&sort=asc")
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))

    episodes = {}
    for episode in soureData.get('data', {}).get('product_list', []):
        episode_number = episode.get('number')
        if episode_number is None:
            continue
        episode_name = episode.get('synopsis', '')
        episode_air_date = None
        ts = episode.get('schedule_start_time')
        if ts:
            try:
                episode_air_date = datetime.fromtimestamp(int(ts)).date()
            except (ValueError, OSError):
                pass
        episode_runtime = None
        dur = episode.get('time_duration')
        if dur:
            episode_runtime = round(int(dur) / 60)
        episode_overview = episode.get('description', '')
        episode_backdrop = episode.get('cover_image_url', '')
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
    return episodes