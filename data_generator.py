# coding= utf-8

url = "https://www.viki.com/tv/37350c-a-man-in-a-veil"

from ast import While
from multiprocessing.sharedctypes import Value
from urllib.parse import urlparse
import urllib.request, json, os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

urlData = urlparse(url)
domain = urlData.netloc
importData = {}
if (domain.endswith("disneyplus.com")): # disney plus ex: https://www.disneyplus.com/zh-hans/series/big-mouth/7kIy3S1m2HNY
    # "zh-Hans"
    language = "zh-Hans"

    seriesID = urlData.path.rsplit('/', 1)[-1]
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
    videoID = urlData.path.rsplit('/', 1)[-1].split('.')[0]
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
    driver = webdriver.Edge(options=options)
    driver.get(url)
    episodes = WebDriverWait(driver, timeout=60).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="li[id*='av-ep-episodes-']"))
    episodeNumber = 1
    for episode in episodes:
        importData[episodeNumber] = {
            "episode_number": episodeNumber,
            "name": episode.find_elements(By.CSS_SELECTOR, value="span[dir='auto']")[0].text,
            "air_date": episode.get_attribute('innerHTML').split('<div>')[1].split('</div>')[0],
            "runtime": episode.get_attribute('innerHTML').split('<div>')[2].split('</div>')[0],
            "overview": episode.find_element(By.CSS_SELECTOR, value="div[data-automation-id*='synopsis'] div[dir='auto']").get_attribute('innerText').split('(C)')[0],
            "backdrop": episode.find_element(By.CSS_SELECTOR, value="noscript").get_attribute('innerText').split('src=\"')[1].split('\"')[0]
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
    mediaID = ''.join(filter(str.isdigit, urlData.path))
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
    containerID = urlData.path.rsplit('/', 1)[-1].split('-')[0]
    page = 1
    while True:
        soureData = json.loads(urllib.request.urlopen(f"https://api.viki.io/v4/containers/{containerID}/episodes.json?token=undefined&per_page=50&page={page}&direction=asc&sort=number&app=100000a").read().decode())
        episodes = soureData["response"]
        for episode in episodes:
            importData[episode["number"]] = {
                "episode_number": episode["number"],
                #"name": episode["long_title"],
                #"air_date": episode["release_date"],
                "runtime": round(episode["duration"]/60),
                "overview": episode["descriptions"][language],
                "backdrop": episode["images"]["poster"]["url"].rsplit('/', 1)[0] + '.jpg'
            }
        
        if (soureData["more"]):
            page = page + 1
        else:
            break

# generator import.csv
if len(importData) > 0:
    import csv
    with open('import.csv', "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = list(list(importData.values())[0].keys()))
        writer.writeheader()
        writer.writerows(importData.values())