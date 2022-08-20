# coding= utf-8-sig
import logging
from datetime import datetime
logging.basicConfig(filename='data_generator.log', level=logging.INFO)

url = "https://www.iqiyi.com/v_19rsn15ux8.html"
logging.info(f"Extracting data from {url} has started")

# same as TMDB
language = "zh-CN"

from urllib.parse import urlparse, parse_qs
import urllib.request, json, os, time, re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

urlData = urlparse(url)
urlPath = urlData.path.rstrip('/')
domain = urlData.netloc

importData = {}
if (domain.endswith("disneyplus.com")): # disney plus ex: https://www.disneyplus.com/zh-hans/series/big-mouth/7kIy3S1m2HNY
    logging.info("disneyplus is detected")
    if language == "":
        language == ""
    else: # default "zh-Hans"
        language = "zh-Hans"

    seriesID = urlPath.rsplit('/', 1)[-1]
    apiRequest = f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/SG/audience/false/maturity/1850/language/{language}/encodedSeriesId/{seriesID}"
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
    episodes = soureData["data"]["DmcSeriesBundle"]["episodes"]["videos"]
    for episode in episodes:
        importData[episode["episodeSequenceNumber"]] = {
            "episode_number": episode["episodeSequenceNumber"],
            "name": episode["text"]["title"]["full"]["program"]["default"]["content"],
            "air_date": episode["releases"][0]["releaseDate"],
            "runtime": round(episode["mediaMetadata"]["runtimeMillis"]/60000),
            "overview": episode["text"]["description"]["full"]["program"]["default"]["content"],
            "backdrop": episode["image"]["thumbnail"]["1.78"]["program"]["default"]["url"]
        }

if (domain.endswith("iqiyi.com")): # iqiyi ex: https://www.iqiyi.com/v_ik3832z0go.html
    logging.info("iqiyi is detected")
    webPage = urllib.request.urlopen(url).read()
    albumId = re.search(r'\"albumId\":(.*?),', str(webPage)).group(1)
    apiRequest = f"https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={albumId}&page=1&size=999&callback="
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
    episodes = soureData["data"]["epsodelist"]
    for episode in episodes:
        episodeNumber = episode["order"]
        importData[episodeNumber] = {
            "episode_number": episodeNumber,
            "name": episode["subtitle"],
            "air_date": episode["period"],
            "runtime": episode["duration"].split(':')[0],
            "overview": episode["description"],
            "backdrop": episode["imageUrl"] #1080*680
        }

        pixel = ("0", "0")
        for imageSize in episode["imageSize"]:
            size = imageSize.split('_')
            if pixel == ("0", "0"):
                pixel =  size
            else:
                if int(size[0]) > int(pixel[0]):
                    pixel = size
        if pixel != ("0", "0"):
            importData[episodeNumber]["backdrop"] = os.path.splitext(importData[episodeNumber]["backdrop"])[0] + f"_imageWidth_imageHeight.jpg?imageWidth={pixel[0]}&imageHeight={pixel[1]}"

if (domain.endswith("mgtv.com")): # mgtv ex: https://w.mgtv.com/b/419629/17004788.html
    logging.info("mgtv is detected")
    videoID =  urlPath.rsplit('/', 1)[-1].split('.')[0]
    apiRequest = f"https://pcweb.api.mgtv.com/episode/list?_support=10000000&version=5.5.35&video_id={videoID}&page=0&size=50&&callback="
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
    episodes = soureData["data"]["list"]
    for episode in episodes:
        if episode["isIntact"] == "1":
            importData[episode["t1"]] = {
                "episode_number": episode["t1"],
                "name": episode["t2"],
                "air_date": episode["ts"].split(' ')[0],
                "runtime": episode["time"].split(':')[0],
                "overview": "",
                "backdrop": episode["img"].rsplit('_', 1)[0] #860*484
            }

if (domain.__contains__("amazon.")): # amazon ex: https://www.amazon.co.jp/%E7%AC%AC02%E8%A9%B1/dp/B07TRLY369/
    options = webdriver.EdgeOptions()
    # load user data
    options.add_argument("user-data-dir=" + os.getcwd() + "\\Selenium") 

    #options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('log-level=3')

    driver = webdriver.Edge(options=options)
    driver.get(url)
    try:
        epExpander = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.CSS_SELECTOR, value="a[data-automation-id='ep-expander']"))
        driver.get(epExpander.get_attribute("href"))
    except:
        pass

    episodes = WebDriverWait(driver, timeout=60).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="li[id*='av-ep-episodes-']"))
    episodeNumber = 1
    for episode in episodes:
        importData[episodeNumber] = {
            "episode_number": episodeNumber,
            "name": episode.find_elements(By.CSS_SELECTOR, value="span[dir='auto']")[0].text.split(' ', 1)[1],
            "air_date": re.findall(r'<div>(.*?)</div>', episode.get_attribute('innerHTML'))[0],
            "runtime": re.findall(r'<div>(.*?)</div>', episode.get_attribute('innerHTML'))[1],
            "overview": episode.find_element(By.CSS_SELECTOR, value="div[data-automation-id*='synopsis'] div[dir='auto']").get_attribute('innerText').split('(C)')[0],
            "backdrop": re.search(r'src=\"(.*?)\"', episode.find_element(By.CSS_SELECTOR, value="noscript").get_attribute('innerText')).group(1)
        }

        episodeNumber = episodeNumber + 1

if (domain.endswith("paravi.jp")): # paravi ex: https://www.paravi.jp/title/64465
    options = webdriver.EdgeOptions()
    # load user data
    options.add_argument("user-data-dir=" + os.getcwd() + "\\Selenium") 
    driver = webdriver.Edge(options=options)
    driver.get(url)
    WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.CSS_SELECTOR, value="i[class='fa-angle_down']")).click()
    episodes = WebDriverWait(driver, timeout=60).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="div[class='card episode-card']"))
    episodeNumber = 1
    for episode in episodes:
        importData[episodeNumber] = {
            "episode_number": episodeNumber,
            "name": episode.find_element(By.CSS_SELECTOR, value="h2[class='title'] p").text,
            #"air_date": episode.get_attribute('innerHTML').split('<div>')[1].split('</div>')[0],
            "runtime": episode.find_element(By.CSS_SELECTOR, value="span[class='duration']").text,
            "overview": episode.find_element(By.CSS_SELECTOR, value="div[class='synopsis']").text,
            "backdrop": episode.find_element(By.CSS_SELECTOR, value="div[class='artwork']").get_attribute('style').split('url(\"')[1].split('?')[0]
        }
        episodeNumber = episodeNumber + 1

if (domain.endswith("bilibili.com")): # bilibili ex: https://www.bilibili.com/bangumi/media/md28234541
    logging.info("bilibili is detected")
    mediaID = ''.join(filter(str.isdigit, urlPath))
    apiRequest = f"https://api.bilibili.com/pgc/review/user?media_id={mediaID}"
    logging.info(f"API request url: {apiRequest}")
    mediaData = json.loads(urllib.request.urlopen(apiRequest).read().decode())

    seasonID = mediaData["result"]["media"]["season_id"]
    apiRequest = f"https://api.bilibili.com/pgc/view/web/season?season_id={seasonID}"
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
    episodes = soureData["result"]["episodes"]
    for episode in episodes:
        importData[episode["title"]] = {
            "episode_number": episode["title"],
            "name": episode["long_title"],
            "air_date": datetime.fromtimestamp(episode["pub_time"]).date(),
            "runtime": round(episode["duration"]/60000),
            "overview": "",
            "backdrop": episode["cover"]
        }

if (domain.endswith("viki.com")): # viki ex: https://www.viki.com/tv/37350c-a-man-in-a-veil
    logging.info("viki is detected")
    language = "en"
    containerID = urlPath.rsplit('/', 1)[-1].split('-')[0]
    page = 1
    while True:
        apiRequest = f"https://api.viki.io/v4/containers/{containerID}/episodes.json?token=undefined&per_page=50&page={page}&direction=asc&sort=number&app=100000a"
        logging.info(f"API request url: {apiRequest}")
        soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
        episodes = soureData["response"]
        for episode in episodes:
            importData[episode["number"]] = {
                "episode_number": episode["number"],
                "name": "",
                "air_date": "",
                "runtime": round(episode["duration"]/60),
                "overview": "",
                "backdrop": episode["images"]["poster"]["url"].rsplit('/', 1)[0] + '.jpg'
            }

            if (importData[episode["number"]].__contains__(language)):
                importData[episode["number"]]["overview"] = episode["descriptions"][language]
        
        if (soureData["more"]):
            page = page + 1
        else:
            break

if (domain.endswith("nhk.jp")): # nhk ex: https://www.nhk.jp/p/comecome/ts/8PMRWK3MGZ
    seriesID = urlPath.rsplit('/', 1)[-1]
    nextURL = f"https://api.nhk.jp/r6/l/tvepisode/ts/{seriesID}.json?offset=0&size=100&order=asc"
    episoideNumber = 1
    while True:
        soureData = json.loads(urllib.request.urlopen(nextURL).read().decode())
        episodes = soureData["result"]
        for episode in episodes:

            importData[episoideNumber] = {
                "episode_number": episoideNumber,
                "name": episode["name"],
                "air_date": episode["releasedEvent"]["startDate"].split('T')[0],
                "runtime": "",
                "overview": episode["description"],
                "backdrop": ""
            }

            if episode.__contains__("eyecatch"):
                importData[episoideNumber]["backdrop"] = episode["eyecatch"]["main"]["url"]

            episoideNumber = episoideNumber + 1
        
        if soureData.__contains__("nextUrl"):
            nextURL = soureData["nextUrl"]
        else:
            break

if (domain.endswith("anidb.net")): # anidb ex: https://anidb.net/anime/2073
    options = webdriver.EdgeOptions()
    # log in to display Japanese title
    options.add_argument("user-data-dir=" + os.getcwd() + "\\Selenium") 

    #options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('log-level=3')

    driver = webdriver.Edge(options=options)
    driver.get(url)
    
    episodes = WebDriverWait(driver, timeout=60).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="tr[itemprop='episode']"))
    for episode in episodes:
        all_columns = episode.find_elements(By.TAG_NAME,"td")
        episodeNumber = all_columns[1].text.strip()
        if episodeNumber.isnumeric():
            importData[episodeNumber] = {
                "episode_number": episodeNumber,
                "name": all_columns[2].find_element(By.CSS_SELECTOR, value="label[itemprop='name']").text,
                "air_date": all_columns[4].get_attribute('content'),
                "runtime": all_columns[3].text,
                "overview": "",
                "backdrop": ""
            }

            try:
                summary = all_columns[2].find_element(By.CSS_SELECTOR, value="span[class='i_icon i_summary']").get_attribute('title')
                importData[episodeNumber]["overview"] = summary.lstrip("Summary: ")
            except:
                pass

if (domain.__contains__("fod.fujitv")): # fod.fujitv: https://fod.fujitv.co.jp/title/4v97/
    seriesID = urlPath.rsplit('/', 1)[-1]
    options = webdriver.EdgeOptions()
    # load user data
    options.add_argument("user-data-dir=" + os.getcwd() + "\\Selenium") 

    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('log-level=3')

    driver = webdriver.Edge(options=options)
    driver.get(url)
    token = driver.get_cookie("CT")["value"]
    userAgent = driver.execute_script("return navigator.userAgent")
    req = urllib.request.Request(f"https://i.fod.fujitv.co.jp/apps/api/lineup/detail/?lu_id={seriesID}&is_premium=false&dv_type=web", headers={'x-authorization': f'Bearer {token}', 'User-Agent' : f'{userAgent}'})
    soureData = json.loads(urllib.request.urlopen(req).read().decode())
    
    episodes = soureData["episodes"]
    episodeNumber = 1
    for episode in episodes:
        importData[episodeNumber] = {
            "episode_number": episodeNumber,
            "name": episode["ep_title"],
            "air_date": "",
            "runtime": episode["duration"],
            "overview": episode["ep_description"].split("\u000d\u000a\u000d\u000a")[0],
            "backdrop": f'https://i.fod.fujitv.co.jp/img/program/{seriesID}/episode/{episode["ep_id"]}_a.jpg'
        }
        episodeNumber = episodeNumber + 1

# language: kr
# backdrop: 1280*720
if (domain.endswith("wavve.com")): # wavve: https://www.wavve.com/player/vod?programid=H04_SP0000054887&page=1
    logging.info("wavve is detected")
    programid = parse_qs(urlData.query)["programid"][0]
    apiRequest = f"https://apis.wavve.com/fz/vod/programs-contents/{programid}?limit=50&offset=0&orderby=old&apikey=E5F3E0D30947AA5440556471321BB6D9&credential=none&device=pc&drm=wm&partner=pooq&pooqzone=none&region=kor&targetage=all"
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
    episodes = soureData["cell_toplist"]["celllist"]
    episodeNumber = 1
    for episode in episodes:
        importData[episodeNumber] = {
            "episode_number": episodeNumber,
            "name": episode["title_list"][0]["text"],
            "air_date": episode["title_list"][1]["text"].rsplit(' ', 1)[-1].split("(")[0],
            "runtime": round(int(episode["_playtime_log"].split(',')[0])/60),
            "overview": episode["synopsis"],
            "backdrop": f"https://{episode['thumbnail']}"
        }

        episodeNumber = episodeNumber + 1 

if (domain.endswith("youku.com")): # youku ex: https://v.youku.com/v_show/id_XNDAzNzE0Mzc2MA==.html
    logging.info("youku is detected")
    episodeID =  re.search(r'id_(.*?)==', url).group(1)
    apiRequest = f"https://api.youku.com/videos/show.json?video_id={episodeID}&ext=show&client_id=3d01f04416cbe807"
    # https://list.youku.com/show/module?id={showid}&tab=showInfo&callback=jQuery
    logging.info(f"API request url: {apiRequest}")
    videoData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
    showID = videoData["show"]["id"]
    page = 1
    episodeNumber = 1
    total = 0
    while True:
        apiRequest = f"https://openapi.youku.com/v2/shows/videos.json?show_id={showID}&show_videotype=%E6%AD%A3%E7%89%87&page={page}&count=30&client_id=3d01f04416cbe807"
        logging.info(f"API request url: {apiRequest}")
        showData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
        if total == 0:
            total = int(showData["total"])
        
        episodes = showData["videos"]
        for episode in episodes:
            episodeID = episode["id"].strip("==")
            try:
                apiRequest = f"https://api.youku.com/videos/show.json?video_id={episodeID}&client_id=3d01f04416cbe807"
                logging.info(f"API request url: {apiRequest}")
                videoData = json.loads(urllib.request.urlopen(apiRequest).read().decode())

                thumbnailUrl = videoData["bigThumbnail"]
                backdrop = thumbnailUrl[0:23] + "F" + thumbnailUrl[24:]

                importData[episodeNumber] = {
                    "episode_number": episodeNumber,
                    "name": "",
                    "air_date": videoData["published"].split(" ")[0],
                    "runtime": round(float(videoData["duration"])/60),
                    "overview": videoData["description"],
                    "backdrop": backdrop,
                }
                episodeNumber = episodeNumber + 1
            except Exception as err:
                logging.error(err)

        if page * 30 > total:
            break
        else:
            page = page + 1

if (domain.endswith("qq.com")): # qq ex: https://v.qq.com/x/cover/mzc00200t0fg7k8/o0043eaefxx.html?ptag=douban.tv
    logging.info("qq is detected")
    cid = urlPath.rsplit('/', 2)[1]
    apiRequest = f"https://access.video.qq.com/fcgi/PlayVidListReq?raw=1&vappid=17174171&vsecret=a06edbd9da3f08db096edab821b3acf3c27ee46e6d57c2fa&page_size=100&type=4&cid={cid}"
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
    episodes = soureData["data"]["vid_list"]
    total_vid = soureData["data"]["total_vid"]
    count_episode = 1
    idlist = ""
    page_size = 30
    for episode in episodes:
        if count_episode % page_size == 1:
            idlist = episode['vid']
        else:
            idlist = idlist + "," + episode['vid']

        if count_episode % page_size == 0 or count_episode == total_vid:
            apiRequest = f"https://union.video.qq.com/fcgi-bin/data?otype=json&tid=682&appid=20001238&appkey=6c03bbe9658448a4&idlist={idlist}&callback="
            logging.info(f"API request url: {apiRequest}")
            videoData = json.loads(urllib.request.urlopen(apiRequest).read().decode().lstrip("QZOutputJson=").rstrip(";"))
            for episodeDate in videoData["results"]:
                # skip previews
                if (episodeDate["fields"]["category_map"][1] == "正片"):
                    episodeNumber = int(episodeDate["fields"]["episode"])
                    importData[episodeNumber] = {
                        "episode_number": episodeNumber,
                        "name": "", #episodeDate["fields"]["title""]
                        "air_date": episodeDate["fields"]["video_checkup_time"].split(" ")[0],
                        "runtime": round(int(episodeDate["fields"]["duration"])/60),
                        "overview": "",
                        "backdrop": episodeDate["fields"]["pic160x90"].rsplit("/", 1)[0],
                    }
        count_episode = count_episode + 1

if (domain.__contains__(".kktv.")): # kktv ex: https://www.kktv.me/titles/01000577
    logging.info("kktv is detected")
    title = urlPath.rsplit('/', 1)[-1]
    apiRequest = f"https://api.kktv.me//api.kktv.me/v3/titles/{title}"
    logging.info(f"API request url: {apiRequest}")
    soureData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
    episodes = soureData["data"]["series"][0]["episodes"]
    episodeNumber = 1
    for episode in episodes:
        importData[episodeNumber] = {
            "episode_number": episodeNumber,
            "name": episode["title"],
            "air_date": datetime.fromtimestamp(episode["publish_time"]).date(),
            "runtime": round(int(episode["duration"])/60),
            "overview": "",
            "backdrop": episode["still"].replace(".xs.",".md.")
        }
        episodeNumber = episodeNumber + 1

logging.info(f"Extracting data is complete")

# generator import.csv
if len(importData) > 0:
    import csv
    with open('import.csv', "w", newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = list(list(importData.values())[0].keys()))
        writer.writeheader()
        writer.writerows(importData.values())