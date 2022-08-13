# coding= gbk

url = "https://www.iqiyi.com/v_ik3832z0go.html"

from urllib.parse import urlparse
import urllib.request, json

urlData = urlparse(url)
domain = urlData.netloc
importData = {}
if (domain.endswith("disneyplus.com")): # disney plus ex: https://www.disneyplus.com/zh-hans/series/big-mouth/7kIy3S1m2HNY
    # "zh-Hans"
    language = "zh-Hans"

    seriesID = urlData.path.rsplit('/', 1)[-1]
    disneyData = json.loads(urllib.request.urlopen(f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/SG/audience/false/maturity/1850/language/{language}/encodedSeriesId/{seriesID}").read().decode())
    episodes = disneyData["data"]["DmcSeriesBundle"]["episodes"]["videos"]
    for episode in episodes:
        episodeSequenceNumber = episode["episodeSequenceNumber"]
        releaseDate = episode["releases"][0]["releaseDate"]
        description = episode["text"]["description"]["full"]["program"]["default"]["content"]
        title = episode["text"]["title"]["full"]["program"]["default"]["content"]
        runtimeMillis = episode["mediaMetadata"]["runtimeMillis"]
        thumbnail = episode["image"]["thumbnail"]["1.78"]["program"]["default"]["url"]
        
        importData[episodeSequenceNumber] = {
            "episode_number": episodeSequenceNumber,
            "name": title,
            "air_date": releaseDate,
            "runtime": round(runtimeMillis/6000),
            "overview": description,
            "backdrop": thumbnail
        }

if (domain.endswith("iqiyi.com")): # iqiyi ex: https://www.iqiyi.com/v_ik3832z0go.html
    webPage = urllib.request.urlopen(url).read()
    albumId = str(webPage).split('\"albumId\":')[1].split(',')[0]
    disneyData = json.loads(urllib.request.urlopen(f"https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={albumId}&page=1&size=999&callback=").read().decode())
    episodes = disneyData["data"]["epsodelist"]
    for episode in episodes:
        order = episode["order"]
        period = episode["period"]
        description = episode["description"]
        subtitle = episode["subtitle"]
        duration = episode["duration"]
        imageUrl = episode["imageUrl"]
        
        importData[order] = {
            "episode_number": order,
            "name": subtitle,
            "air_date": period,
            "runtime": duration.split(':')[0],
            "overview": description,
            "backdrop": imageUrl.replace(".jpg", "_1920_1080.jpg")
        }


# generator import.csv
if len(importData) > 0:
    import csv
    with open('import.csv', "w", newline='', encoding='gbk') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = list(list(importData.values())[0].keys()))
        writer.writeheader()
        writer.writerows(importData.values())