# coding= gbk

url = "https://www.disneyplus.com/zh-hans/series/big-mouth/7kIy3S1m2HNY"

# "zh-Hans"
language = "zh-Hans"

from urllib.parse import urlparse
import urllib.request, json

urlData = urlparse(url)
domain = urlData.netloc
importData = {}
if (domain.endswith("disneyplus.com")): # disney
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
import csv
with open('import.csv', "w", newline='', encoding='UTF') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = list(list(importData.values())[0].keys()))
    writer.writeheader()
    writer.writerows(importData.values())
    for value in importData.values():
        print(value)