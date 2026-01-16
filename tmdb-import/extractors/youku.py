import json
import logging
import re
from ..common import Episode, open_url, ini_playwright_page, cleanup_playwright_page
from urllib.parse import urlparse, parse_qs

def youku_extractor(url):
    logging.info("youku_extractor is called")
    client_id = "0dec1b5a3cb570c1"
    
    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query)
    show_param = qs.get("s", [None])[0]
    vid_param = qs.get("vid", [None])[0]
    
    if show_param:
        showID = show_param
    elif vid_param or "video?" in url:
        episodeID = vid_param or re.search(r'id_(.*?)\.html', url).group(1).rstrip("==")
        videoData = json.loads(open_url(f"https://api.youku.com/videos/show.json?video_id={episodeID}&ext=show&client_id={client_id}&package=com.huawei.hwvplayer.youku"))
        showID = videoData.get("show", {}).get("id") or episodeID
    else:
        showID = re.search(r'id_(.*?)\.html', url).group(1).rstrip("==")
    
    logging.info(f"show id: {showID}")
    show_data = json.loads(open_url(f"https://openapi.youku.com/v2/shows/show.json?show_id={showID}&client_id={client_id}&package=com.huawei.hwvplayer.youku"))
    
    if "error" in show_data:
        logging.info(f"Show API failed with video ID, extracting show id from page...")
        import time
        page = ini_playwright_page(headless=True, images=False)
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(3)
            html = page.content()
            script_matches = re.findall(r'showId["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)', html)
            if script_matches:
                showID = script_matches[0]
                logging.info(f"Extracted show id from page: {showID}")
                show_data = json.loads(open_url(f"https://openapi.youku.com/v2/shows/show.json?show_id={showID}&client_id={client_id}&package=com.huawei.hwvplayer.youku"))
            else:
                link_matches = re.findall(r'/show_page/id_([a-zA-Z0-9_-]+)\.html', html)
                if link_matches:
                    showID = link_matches[0]
                    logging.info(f"Extracted show id from page links: {showID}")
                    show_data = json.loads(open_url(f"https://openapi.youku.com/v2/shows/show.json?show_id={showID}&client_id={client_id}&package=com.huawei.hwvplayer.youku"))
                else:
                    logging.error("Failed to extract show id from page")
                    return {}
        except Exception as e:
            logging.error(f"Failed to extract from page: {e}")
            return {}
        finally:
            cleanup_playwright_page(page)
    
    if "error" in show_data:
        logging.error(f"API returned error: {show_data}")
        return {}
    
    logging.info(f"show link: {show_data['link']}")
    logging.info(f"name: {show_data['name']}")
    logging.info(f"poster url: {show_data['poster_large']}")
    logging.info(f"backdrop url: {show_data['thumbnail_large']}")
    logging.info(f"description url: {show_data['description']}")
    
    episodes = {}
    episodeNumber = 1
    page = 1
    total = 0
    
    while True:
        showData = json.loads(open_url(f"https://openapi.youku.com/v2/shows/videos.json?show_id={showID}&show_videotype=%E6%AD%A3%E7%89%87&page={page}&count=30&client_id={client_id}&package=com.huawei.hwvplayer.youku"))
        if total == 0:
            total = int(showData["total"])

        for episode in showData["videos"]:
            episodeID = episode["id"].strip("==")
            try:
                videoData = json.loads(open_url(f"https://api.youku.com/videos/show.json?video_id={episodeID}&client_id={client_id}&package=com.huawei.hwvplayer.youku"))
                episode_name = episode.get("rc_title") or videoData["title"]
                episode_air_date = videoData["published"].split(" ")[0]
                episode_runtime = round(float(videoData["duration"]) / 60)
                episode_overview = videoData["description"]
                episode_backdrop = videoData["bigThumbnail"][0:23] + "F" + videoData["bigThumbnail"][24:]
                episodes[episodeNumber] = Episode(episodeNumber, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
                episodeNumber += 1
            except Exception as err:
                logging.error(err)

        if page * 30 > total:
            break
        page += 1

    return episodes