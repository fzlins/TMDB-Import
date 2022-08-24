from urllib.parse import urlparse
import re

# https://www.themoviedb.org/tv/106064/season/1
def import_from_url(url, language="zh-CN"):  
    try:
        urlData = urlparse(url)
        tmdb_id = re.search(r'tv/(.*?)/', urlData.path).group(1)  
        if not tmdb_id.isdigit():
            raise
        season_number = re.search(r'season/(.*?)(/|$)', urlData.path).group(1)

        if not season_number.isdigit():
            raise

        from .importors.episode import import_spisode
        import_spisode(tmdb_id, season_number)

    except:
        print(f"Invalid TMDB url {url}")
        return
