import json
import urllib.request
from urllib.parse import urlparse
import logging
from ..common import Episode, ini_playwright_page, cleanup_playwright_page, open_url

# ex: https://fod.fujitv.co.jp/title/4v97/
def fod_extractor(url):
    logging.info("fod_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')

    seriesID = urlPath.rsplit('/', 1)[-1]

    page = ini_playwright_page()
    page.goto(url)
    
    # Get cookies from context
    cookies = page.context.cookies()
    ct_cookie = next((cookie for cookie in cookies if cookie['name'] == 'CT'), None)
    if not ct_cookie:
        cleanup_playwright_page(page)
        raise ValueError("CT cookie not found")
    token = ct_cookie['value']
    
    # Get user agent using page.evaluate()
    userAgent = page.evaluate("() => navigator.userAgent")
    
    cleanup_playwright_page(page)

    apiRequest = urllib.request.Request(f"https://i.fod.fujitv.co.jp/apps/api/lineup/detail/?lu_id={seriesID}&is_premium=false&dv_type=web", headers={'x-authorization': f'Bearer {token}', 'User-Agent' : f'{userAgent}'})
    soureData = json.loads(open_url(apiRequest))

    season_name = soureData["detail"]["lu_title"]
    logging.info(f"name: {season_name}")
    season_overview = soureData["detail"]["description"]
    logging.info(f"overview: {season_overview}")
    season_backdrop = f'https://i.fod.fujitv.co.jp/img/program/{seriesID}/{seriesID}_a.jpg'
    logging.info(f"backdrop: {season_backdrop}")
    
    episodes = {}
    episodeNumber = 1
    for episode in soureData["episodes"]:
        episode_number = episodeNumber
        episode_name = episode["ep_title"]
        if episode_name.startswith('#'):
            episode_name = episode_name.removeprefix(f'#{episode_number}').lstrip()
        episode_air_date = ""
        episode_runtime = episode["duration"]
        episode_overview = episode["ep_description"].split("\u000d\u000a\u000d\u000a")[0]
        episode_backdrop = f'https://i.fod.fujitv.co.jp/img/program/{seriesID}/episode/{episode["ep_id"]}_a.jpg'
        
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
        episodeNumber = episodeNumber + 1

    return episodes