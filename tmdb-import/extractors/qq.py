import json
import logging
import re
from ..common import Episode, open_url

# ex: https://v.qq.com/x/cover/mzc00200t0fg7k8/o0043eaefxx.html?ptag=douban.tv
# ex: https://v.qq.com/x/cover/mzc00200t0fg7k8.html
def qq_extractor(url):
    logging.info("qq_extractor is called")
    
    cid_match = re.search(r'/cover/([^/.]+)', url)
    if not cid_match:
        raise ValueError("Could not extract cid from the URL")
    cid = cid_match.group(1)
    
    apiRequest = f"https://data.video.qq.com/fcgi-bin/data?otype=json&tid=431&idlist={cid}&appid=10001005&appkey=0d1a9ddd94de871b"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest).lstrip("QZOutputJson=").rstrip(";"))
    
    episodes = {}
    video_ids = soureData["results"][0]["fields"]["video_ids"]
    
    episode_counter = 1
    page_size = 30
    current_batch = []
    
    for vid in video_ids:
        current_batch.append(vid)
        
        if len(current_batch) == page_size or vid == video_ids[-1]:
            idlist = ",".join(current_batch)
            
            apiRequest = f"https://union.video.qq.com/fcgi-bin/data?otype=json&tid=682&appid=20001238&appkey=6c03bbe9658448a4&idlist={idlist}&callback="
            logging.debug(f"API request url: {apiRequest}")
            videoData = json.loads(open_url(apiRequest).lstrip("QZOutputJson=").rstrip(";"))
            
            for episodeData in videoData["results"]:
                category_map = episodeData["fields"]["category_map"]
                
                if len(category_map) > 1 and category_map[1] == "正片":
                    episode_number_raw = int(episodeData["fields"]["episode"])
                    vid = episodeData["fields"]["vid"]
                    
                    if episode_number_raw == 0:
                        episode_number = episode_counter
                        episode_counter += 1
                    else:
                        episode_number = episode_number_raw
                        if episode_number >= episode_counter:
                            episode_counter = episode_number + 1
                    
                    apiRequest = f"https://node.video.qq.com/x/api/float_vinfo2?vid={vid}"
                    logging.debug(f"API request url: {apiRequest}")
                    
                    vinfo_data = json.loads(open_url(apiRequest))
                    video_info = vinfo_data.get("c", {})
                    
                    second_title = video_info.get("second_title")
                    title = video_info.get("title")
                    
                    episode_name = second_title or title or ""
                    episode_name = re.sub(r'_\d+$', '', episode_name)
                    episode_name = re.sub(r'^第\d+集\s*', '', episode_name)
                    
                    pic_data = video_info.get("pic", "")
                    episode_backdrop = pic_data.replace("/160", "/1280") if pic_data else ""
                    
                    episode_air_date = episodeData["fields"]["video_checkup_time"].split(" ")[0]
                    episode_runtime = round(int(episodeData["fields"]["duration"]) / 60)
                    
                    episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, "", episode_backdrop)
            
            current_batch = []
    
    titles = [ep.name for ep in episodes.values() if ep.name]
    if titles and len(set(titles)) == 1:
        for ep in episodes.values():
            ep.name = ""
    
    return episodes