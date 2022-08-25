import json
import logging
import re
from ..common import Episode, open_url

# ex: https://v.qq.com/x/cover/mzc00200t0fg7k8/o0043eaefxx.html?ptag=douban.tv
def qq_extractor(url):
    logging.info("qq_extractor is called")
    cid = re.search(r'/cover/(.*?)/', url).group(1)
    apiRequest = f"https://access.video.qq.com/fcgi/PlayVidListReq?raw=1&vappid=17174171&vsecret=a06edbd9da3f08db096edab821b3acf3c27ee46e6d57c2fa&page_size=100&type=4&cid={cid}"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    
    episodes = {}
    total_vid = soureData["data"]["total_vid"]
    count_episode = 1
    idlist = ""
    page_size = 30
    for episode in soureData["data"]["vid_list"]:
        if count_episode % page_size == 1:
            idlist = episode['vid']
        else:
            idlist = idlist + "," + episode['vid']

        if count_episode % page_size == 0 or count_episode == total_vid:
            apiRequest = f"https://union.video.qq.com/fcgi-bin/data?otype=json&tid=682&appid=20001238&appkey=6c03bbe9658448a4&idlist={idlist}&callback="
            logging.debug(f"API request url: {apiRequest}")
            videoData = json.loads(open_url(apiRequest).lstrip("QZOutputJson=").rstrip(";"))
            for episodeDate in videoData["results"]:
                # skip previews
                if (episodeDate["fields"]["category_map"][1] == "正片"):
                    episode_number = int(episodeDate["fields"]["episode"])
                    episode_name = "" #episodeDate["fields"]["title""]
                    episode_air_date = episodeDate["fields"]["video_checkup_time"].split(" ")[0]
                    episode_runtime = round(int(episodeDate["fields"]["duration"])/60)
                    episode_overview = ""
                    episode_backdrop = episodeDate["fields"]["pic160x90"].rsplit("/", 1)[0]
                    episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)

        count_episode = count_episode + 1
    
    return episodes