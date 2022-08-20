import json
from ..extractor import Episode
from urllib.parse import urlparse, parse_qs
# language: kr
# backdrop: 1280*720
url = f"https://www.wavve.com/player/vod?programid=H04_SP0000054887&page=1"
#logging.info("wavve is detected")
urlData = urlparse(url)
urlPath = urlData.path.rstrip('/')
programid = parse_qs(urlData.query)["programid"][0]
apiRequest = f"https://apis.wavve.com/fz/vod/programs-contents/{programid}?limit=50&offset=0&orderby=old&apikey=E5F3E0D30947AA5440556471321BB6D9&credential=none&device=pc&drm=wm&partner=pooq&pooqzone=none&region=kor&targetage=all"
#logging.info(f"API request url: {apiRequest}")
sourceData = json.loads(urllib.request.urlopen(apiRequest).read().decode())
episodes = {}
episodeNumber = 1
for source in sourceData["cell_toplist"]["celllist"]:
    name = source["title_list"][0]["text"]
    air_date = source["title_list"][1]["text"].rsplit(' ', 1)[-1].split("(")[0]
    runtime = round(int(source["_playtime_log"].split(',')[0])/60)
    overview = source["synopsis"]
    backdrop = f"https://{source['thumbnail']}"

    episodes[episodeNumber] = Episode(name, air_date, runtime, overview, backdrop)
    episodeNumber = episodeNumber + 1 
