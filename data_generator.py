# coding= gbk

url = "https://w.mgtv.com/b/419629/17004788.html"

from urllib.parse import urlparse
import urllib.request, json

urlData = urlparse(url)
domain = urlData.netloc
importData = {}
if (domain.endswith("disneyplus.com")): # disney plus ex: https://www.disneyplus.com/zh-hans/series/big-mouth/7kIy3S1m2HNY
    # "zh-Hans"
    language = "zh-Hans"

    seriesID = urlData.path.rsplit('/', 1)[-1]
    iqiyiData = json.loads(urllib.request.urlopen(f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/SG/audience/false/maturity/1850/language/{language}/encodedSeriesId/{seriesID}").read().decode())
    episodes = iqiyiData["data"]["DmcSeriesBundle"]["episodes"]["videos"]
    for episode in episodes:
        importData[episode["episodeSequenceNumber"]] = {
            "episode_number": episode["episodeSequenceNumber"],
            "name": episode["text"]["title"]["full"]["program"]["default"]["content"],
            "air_date": episode["releases"][0]["releaseDate"],
            "runtime": round(episode["mediaMetadata"]["runtimeMillis"]/6000),
            "overview": episode["text"]["description"]["full"]["program"]["default"]["content"],
            "backdrop": episode["image"]["thumbnail"]["1.78"]["program"]["default"]["url"]
        }

if (domain.endswith("iqiyi.com")): # iqiyi ex: https://www.iqiyi.com/v_ik3832z0go.html
    webPage = urllib.request.urlopen(url).read()
    albumId = str(webPage).split('\"albumId\":')[1].split(',')[0]
    iqiyiData = json.loads(urllib.request.urlopen(f"https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={albumId}&page=1&size=999&callback=").read().decode())
    episodes = iqiyiData["data"]["epsodelist"]
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
    mgtvData = json.loads(urllib.request.urlopen(f"https://pcweb.api.mgtv.com/episode/list?_support=10000000&version=5.5.35&video_id={videoID}&page=0&size=50&&callback=").read().decode())
    episodes = mgtvData["data"]["list"]
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

# generator import.csv
if len(importData) > 0:
    import csv
    with open('import.csv', "w", newline='', encoding='gbk') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = list(list(importData.values())[0].keys()))
        writer.writeheader()
        writer.writerows(importData.values())