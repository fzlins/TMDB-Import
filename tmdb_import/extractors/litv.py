import json
import logging
from urllib.parse import urlparse
from ..common import Episode, Metadata, Season, open_url

# ex: https://www.litv.tv/comic/watch/VOD00366591
def litv_extractor(url):
    logging.info("litv_extractor is called")
    
    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')
    
    # 解析URL获取content-type和content-id
    # 格式: /comic/watch/VOD00366591
    path_parts = urlPath.split('/')
    if len(path_parts) < 3:
        logging.error(f"Invalid LiTV URL format: {url}")
        return Metadata(url=url, seasons=[])
    
    content_type = path_parts[0]  # 例如: comic
    content_id = path_parts[2]     # 例如: VOD00366591
    
    # 构建API URL
    # 注意: 322e31362e3134 是版本号，可能需要动态获取或更新
    build_id = "322e31362e3134"
    api_url = f"https://www.litv.tv/_next/data/{build_id}/{content_type}/watch/{content_id}.json?content-type={content_type}&content-id={content_id}"
    
    logging.debug(f"API request url: {api_url}")
    
    try:
        response_data = json.loads(open_url(api_url))
        
        # 解析数据结构 - 只使用seriesTree
        page_props = response_data.get("pageProps", {})
        series_tree = page_props.get("seriesTree", {})
        
        # 获取标题
        title = series_tree.get("title", "")
        logging.info(f"Title: {title}")
        
        # 获取所有季
        seasons = series_tree.get("seasons", [])

        season_list = []

        if seasons and len(seasons) > 0:
            # 遍历所有季
            for season_data in seasons:
                season_number = season_data.get("season") or None
                season_name = season_data.get("season_name", "")
                episodes_data = season_data.get("episodes", [])

                logging.info(f"Processing {season_name} with {len(episodes_data)} episodes")

                season_eps = {}
                for episode_data in episodes_data:
                    # 使用episode字段作为集数
                    episode_num_str = episode_data.get("episode", "")
                    if not episode_num_str:
                        logging.warning(f"Episode number missing, skipping")
                        continue

                    try:
                        episode_num = int(episode_num_str)
                    except (ValueError, TypeError):
                        logging.warning(f"Invalid episode number: {episode_num_str}, skipping")
                        continue

                    # 排除预告片（episode为0）
                    if episode_num == 0:
                        logging.debug(f"Skipping preview episode")
                        continue

                    episode_number = episode_num

                    # 获取集名称 - 优先使用secondary_mark（包含副标题），否则使用episode_name
                    episode_name = episode_data.get("secondary_mark", "") or episode_data.get("episode_name", "")

                    # 获取剧集图片
                    video_image = episode_data.get("video_image", "")
                    episode_backdrop = f"https://p-cdnstatic.svc.litv.tv/{video_image}" if video_image and not video_image.startswith("http") else video_image

                    # seriesTree中没有播出日期信息，留空
                    episode_air_date = ""

                    # 时长和描述信息在seriesTree中不存在，留空
                    episode_runtime = ""
                    episode_overview = ""

                    season_eps[episode_number] = Episode(
                        episode_number,
                        episode_name,
                        episode_air_date,
                        episode_runtime,
                        episode_overview,
                        episode_backdrop
                    )
                season_list.append(Season(season_number, episodes=season_eps))

        total_episodes = sum(len(s.episodes) for s in season_list)
        logging.info(f"Extracted {total_episodes} episode(s) from {len(season_list)} season(s)")
        return Metadata(url=url, language="zh-TW", name=title, seasons=season_list)
        
    except Exception as e:
        logging.error(f"Error extracting data from LiTV: {e}")
        return Metadata(url=url, seasons=[])
