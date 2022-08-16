# coding= utf-8-sig
import logging
from unicodedata import name
logging.basicConfig(filename='data_generator.log', level=logging.INFO)

url = "https://www.amazon.co.jp/12-%E9%89%84%E3%82%92%E3%81%8F%E3%81%84%E3%81%AD%E3%81%88%E3%81%AE%E5%B7%BB%EF%BC%8F%E3%81%8A%E3%82%89%E3%82%A4%E3%82%AB%E3%83%83%E3%81%9F%E3%81%A9%E3%81%AE%E5%B7%BB/dp/B087CYC22Y/"
logging.info(f"Extracting data from {url} has started")

# same as TMDB
language = "zh-CN"

from urllib.parse import urlparse
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
    if language == "":
        language == ""
    else: # default "zh-Hans"
        language = "zh-Hans"

    seriesID = urlPath.rsplit('/', 1)[-1]
    soureData = json.loads(urllib.request.urlopen(f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/SG/audience/false/maturity/1850/language/{language}/encodedSeriesId/{seriesID}").read().decode())
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
    webPage = urllib.request.urlopen(url).read()
    albumId = str(webPage).split('\"albumId\":')[1].split(',')[0]
    soureData = json.loads(urllib.request.urlopen(f"https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={albumId}&page=1&size=999&callback=").read().decode())
    episodes = soureData["data"]["epsodelist"]
    for episode in episodes:
        importData[episode["order"]] = {
            "episode_number": episode["order"],
            "name": episode["subtitle"],
            "air_date": episode["period"],
            "runtime": episode["duration"].split(':')[0],
            "overview": episode["description"],
            "backdrop": episode["imageUrl"].replace(".jpg", "_1280_720.jpg") #1080*680
        }

if (domain.endswith("mgtv.com")): # mgtv ex: https://w.mgtv.com/b/419629/17004788.html
    videoID = urlPath.rsplit('/', 1)[-1].split('.')[0]
    soureData = json.loads(urllib.request.urlopen(f"https://pcweb.api.mgtv.com/episode/list?_support=10000000&version=5.5.35&video_id={videoID}&page=0&size=50&&callback=").read().decode())
    episodes = soureData["data"]["list"]
    for episode in episodes:
        if episode["isIntact"] == "1":
            importData[episode["t1"]] = {
                "episode_number": episode["t1"],
                "name": episode["t2"],
                "air_date": episode["ts"].split(' ')[0],
                "runtime": episode["time"].split(':')[0],
                "overview": "",
                "backdrop": episode["img"].split('.jpg_')[0] + ".jpg_1280x720.jpg" #860*484
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
    mediaID = ''.join(filter(str.isdigit, urlPath))
    mediaData = json.loads(urllib.request.urlopen(f"https://api.bilibili.com/pgc/review/user?media_id={mediaID}").read().decode())
    seasonID = mediaData["result"]["media"]["season_id"]
    soureData = json.loads(urllib.request.urlopen(f"https://api.bilibili.com/pgc/view/web/season?season_id={seasonID}").read().decode())
    episodes = soureData["result"]["episodes"]
    for episode in episodes:
        importData[episode["title"]] = {
            "episode_number": episode["title"],
            "name": episode["long_title"],
            "air_date": episode["release_date"],
            "runtime": round(episode["duration"]/60000),
            "overview": "",
            "backdrop": episode["cover"]
        }

if (domain.endswith("viki.com")): # viki ex: https://www.viki.com/tv/37350c-a-man-in-a-veil
    language = "en"
    containerID = urlPath.rsplit('/', 1)[-1].split('-')[0]
    page = 1
    while True:
        soureData = json.loads(urllib.request.urlopen(f"https://api.viki.io/v4/containers/{containerID}/episodes.json?token=undefined&per_page=50&page={page}&direction=asc&sort=number&app=100000a").read().decode())
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

# not ready
if (domain.endswith("youku.com")): # youku ex: https://v.youku.com/v_show/id_XNDAzNzE0Mzc2MA==.html
    options = webdriver.EdgeOptions()
    # load user data
    options.add_argument("user-data-dir=" + os.getcwd() + "\\Selenium") 

    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--mute-audio')
    options.add_argument('log-level=3')
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

    driver = webdriver.Edge(options=options)

    driver.get(url)
    showid = re.search(r'showid_en:(.*?),', driver.page_source).group(1).replace('\'', '').strip()
    driver.get(f"https://list.youku.com/show/module?id={showid}&tab=showInfo&callback=jQuery")
    episodesURL = re.search(r'&lt;ul class(.*?)ul&gt;&lt;', driver.page_source).group(1)

    for episode in re.findall(r'id_(.*?).html', episodesURL):
        episodeURL = f'https://v.youku.com/v_show/id_{episode}.html'
        logging.info(f"Extracting data from {episodeURL}")
        driver.get(episodeURL)
        irAlbumName = driver.find_element(By.CSS_SELECTOR, "meta[name='irAlbumName']").get_attribute('content')
        irTitle = driver.find_element(By.CSS_SELECTOR, "meta[name='irTitle']").get_attribute('content')
        episodeNumber = ''.join(filter(str.isdigit, irTitle.replace(irAlbumName, "")))
        thumbnailUrl = driver.find_element(By.CSS_SELECTOR, "meta[itemprop='thumbnailUrl']").get_attribute('content')
        backdrop = thumbnailUrl[0:23] + "F" + thumbnailUrl[24:]

        importData[episodeNumber] = {
            "episode_number": episodeNumber,
            "name": driver.find_element(By.CSS_SELECTOR, "meta[property='og:title']").get_attribute('content').replace(irAlbumName, ""),
            "air_date": driver.find_element(By.CSS_SELECTOR, "meta[itemprop='datePublished']").get_attribute('content').split(' ')[0],
            "runtime": "",
            "overview": driver.find_element(By.CSS_SELECTOR, "meta[name='description']").get_attribute('content').split('视频内容简介:')[1],
            "backdrop": backdrop,
        }

logging.info(f"Extracting data from {url} is complete")

# generator import.csv
if len(importData) > 0:
    import csv
    with open('import.csv', "w", newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = list(list(importData.values())[0].keys()))
        writer.writeheader()
        writer.writerows(importData.values())