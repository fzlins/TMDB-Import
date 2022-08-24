from urllib.parse import urlparse, parse_qs
import re

# https://www.themoviedb.org/tv/106064/season/1
def import_from_url(url):  
    try:
        urlData = urlparse(url)
        tmdb_id = re.search(r'tv/(.*?)/', urlData.path).group(1).split('-')[0]
        
        if not tmdb_id.isdigit():
            raise
        season_number = re.search(r'season/(.*?)(/|$)', urlData.path).group(1)

        if not season_number.isdigit():
            raise
        
        language = ""
        urlQuery = parse_qs(urlData.query)
        if urlQuery.__contains__("language"):
            language = urlQuery["language"][0]
    except Exception as err:
        print(f"Invalid TMDB url {url}")
        return
    from .importors.episode import import_spisode
    import_spisode(tmdb_id, season_number, language)
