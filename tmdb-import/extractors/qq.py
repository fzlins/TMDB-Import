import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..common import Episode, open_url

# ex: https://v.qq.com/x/cover/mzc00200t0fg7k8/o0043eaefxx.html?ptag=douban.tv
# ex: https://v.qq.com/x/cover/mzc00200t0fg7k8.html
def qq_extractor(url):
    logging.info("qq_extractor is called")
    
    cid_match = re.search(r'/cover/([^/.]+)', url)
    if not cid_match:
        raise ValueError("Could not extract cid from the URL")
    cid = cid_match.group(1)
    
    # 辅助函数：转换图片URL为高清版本
    def get_hd_pic(pic_url):
        if pic_url:
            return pic_url.replace("/160", "/1280")
        return ""
    
    # 辅助函数：清理标题
    def clean_title(title):
        if not title:
            return ""
        title = re.sub(r'_\d+$', '', title)  # 移除结尾的 _数字
        title = re.sub(r'^第\d+集\s*', '', title)  # 移除开头的 第X集
        return title
    
    apiRequest = f"https://data.video.qq.com/fcgi-bin/data?otype=json&tid=431&idlist={cid}&appid=10001005&appkey=0d1a9ddd94de871b"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest).lstrip("QZOutputJson=").rstrip(";"))
    
    episodes = {}
    video_ids = soureData["results"][0]["fields"]["video_ids"]
    
    episode_counter = 1
    page_size = 30
    current_batch = []
    
    # 第一阶段：收集所有正片的基本信息
    episode_base_info = []
    
    for vid in video_ids:
        current_batch.append(vid)
        
        if len(current_batch) == page_size or vid == video_ids[-1]:
            idlist = ",".join(current_batch)
            
            apiRequest = f"https://union.video.qq.com/fcgi-bin/data?otype=json&tid=682&appid=20001238&appkey=6c03bbe9658448a4&idlist={idlist}&callback="
            logging.debug(f"API request url: {apiRequest}")
            videoData = json.loads(open_url(apiRequest).lstrip("QZOutputJson=").rstrip(";"))
            
            for episodeData in videoData["results"]:
                category_map = episodeData["fields"]["category_map"]
                
                if any(isinstance(item, str) and "正片" in item for item in category_map):
                    episode_number_raw = int(episodeData["fields"]["episode"])
                    vid = episodeData["fields"]["vid"]
                    
                    if episode_number_raw == 0:
                        episode_number = episode_counter
                        episode_counter += 1
                    else:
                        episode_number = episode_number_raw
                        if episode_number >= episode_counter:
                            episode_counter = episode_number + 1
                    
                    # 从union API获取图片作为备用
                    fallback_pic = get_hd_pic(episodeData["fields"].get("pic160x90", ""))
                    
                    episode_base_info.append({
                        "episode_number": episode_number,
                        "vid": vid,
                        "episode_air_date": episodeData["fields"]["video_checkup_time"].split(" ")[0],
                        "episode_runtime": round(int(episodeData["fields"]["duration"]) / 60),
                        "fallback_pic": fallback_pic
                    })
            
            current_batch = []
    
    logging.info(f"Found {len(episode_base_info)} episodes, fetching details...")
    
    # 第二阶段：并发获取所有剧集的详细信息（标题和更好的图片）
    def fetch_episode_detail(info):
        vid = info["vid"]
        apiRequest = f"https://node.video.qq.com/x/api/float_vinfo2?vid={vid}"
        logging.debug(f"API request url: {apiRequest}")
        
        try:
            vinfo_data = json.loads(open_url(apiRequest))
            video_info = vinfo_data.get("c", {})
            
            second_title = video_info.get("second_title")
            title = video_info.get("title")
            
            episode_name = clean_title(second_title or title or "")
            
            # 优先使用float_vinfo2的图片，失败则使用备用图片
            pic_data = video_info.get("pic", "")
            episode_backdrop = get_hd_pic(pic_data) if pic_data else info["fallback_pic"]
            
            return {
                "episode_number": info["episode_number"],
                "episode_name": episode_name,
                "episode_backdrop": episode_backdrop,
                "episode_air_date": info["episode_air_date"],
                "episode_runtime": info["episode_runtime"]
            }
        except Exception as e:
            logging.warning(f"Failed to fetch detail for vid {vid}: {e}, using fallback data")
            return {
                "episode_number": info["episode_number"],
                "episode_name": "",
                "episode_backdrop": info["fallback_pic"],  # 使用备用图片
                "episode_air_date": info["episode_air_date"],
                "episode_runtime": info["episode_runtime"]
            }
    
    # 使用线程池并发请求，最多15个并发（测试显示安全且更快）
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(fetch_episode_detail, info) for info in episode_base_info]
        
        for future in as_completed(futures):
            result = future.result()
            episodes[result["episode_number"]] = Episode(
                result["episode_number"],
                result["episode_name"],
                result["episode_air_date"],
                result["episode_runtime"],
                "",
                result["episode_backdrop"]
            )
    
    # 如果所有剧集标题都相同（通常是剧名），则清空所有标题
    titles = [ep.name for ep in episodes.values() if ep.name]
    if titles and len(set(titles)) == 1:
        logging.info(f"All episodes have same title '{titles[0]}', clearing titles")
        for ep in episodes.values():
            ep.name = ""
    
    logging.info(f"Successfully extracted {len(episodes)} episodes")
    return episodes