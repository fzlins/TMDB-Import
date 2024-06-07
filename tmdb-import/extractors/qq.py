import json
import logging
import re
import time
from ..common import Episode, open_url

# ex: https://v.qq.com/x/cover/mzc00200t0fg7k8/o0043eaefxx.html?ptag=douban.tv
def qq_extractor(url):
    logging.info("qq_extractor is called")
    cid = re.search(r'/cover/(.*?)/', url).group(1)
    apiRequest = f"https://data.video.qq.com/fcgi-bin/data?otype=json&tid=431&idlist={cid}&appid=10001005&appkey=0d1a9ddd94de871b"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest).lstrip("QZOutputJson=").rstrip(";"))
    
    episodes = {}
    total_vid = len(soureData["results"][0]["fields"]["video_ids"])
    logging.debug(total_vid)
    count_episode = 1
    idlist = ""
    page_size = 30
    for episode in soureData["results"][0]["fields"]["video_ids"]:
        if count_episode % page_size == 1:
            idlist = episode
        else:
            idlist = idlist + "," + episode

        if count_episode % page_size == 0 or count_episode == total_vid:
            apiRequest = f"https://union.video.qq.com/fcgi-bin/data?otype=json&tid=682&appid=20001238&appkey=6c03bbe9658448a4&idlist={idlist}&callback="
            logging.debug(f"API request url: {apiRequest}")
            videoData = json.loads(open_url(apiRequest).lstrip("QZOutputJson=").rstrip(";"))
            for episodeDate in videoData["results"]:
                # skip previews
                if (episodeDate["fields"]["category_map"][1] == "正片"):
                    episode_number = int(episodeDate["fields"]["episode"])
                    vid = episodeDate["fields"]["vid"]
                    apiRequest = f"https://node.video.qq.com/x/api/float_vinfo2?vid={vid}"
                    logging.debug(f"API request url: {apiRequest}")
                    episode_name = json.loads(open_url(apiRequest))["c"]["second_title"]
                    time.sleep(0.5)
                    episode_air_date = episodeDate["fields"]["video_checkup_time"].split(" ")[0]
                    episode_runtime = round(int(episodeDate["fields"]["duration"])/60)
                    episode_overview = ""
                    episode_backdrop = "" #episodeDate["fields"]["pic160x90"].rsplit("/", 1)[0]
                    episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

        count_episode = count_episode + 1
    
    return episodes
