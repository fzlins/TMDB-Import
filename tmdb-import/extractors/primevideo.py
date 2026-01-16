import json, logging, re
from datetime import datetime
from ..common import Episode, ini_playwright_page, cleanup_playwright_page

def _extract_episode_data(page):
    for script in page.locator("script").all():
        try:
            if (content := script.text_content()) and len(content) > 1000 and "episodeNumber" in content:
                for item in json.loads(content).get("props", {}).get("body", []):
                    if isinstance(item, dict):
                        detail_obj = item.get("props", {}).get("btf", {}).get("state", {}).get("detail", {}).get("detail", {})
                        if isinstance(detail_obj, dict):
                            return {tid: td for tid, td in detail_obj.items() if isinstance(td, dict) and td.get("episodeNumber")}
        except: pass
    return {}

def _parse_episode(ep_data, season_num=0):
    if not (ep_num := ep_data.get("episodeNumber", "")): return None
    key = f"S{season_num}E{ep_num}" if season_num else str(ep_num)
    return Episode(key, ep_data.get("title", ""),
                   _parse_date(ep_data.get("releaseDate", "")), _parse_runtime(ep_data.get("runtime", "")),
                   ep_data.get("synopsis", ""), ep_data.get("images", {}).get("packshot") or ep_data.get("images", {}).get("covershot") or "")

def _parse_date(d):
    if not d: return ""
    try:
        if "年" in d: d = d.replace("年", "-").replace("月", "-").replace("日", "")
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']:
            try: return datetime.strptime(d, fmt).date()
            except ValueError: continue
    except: pass
    return ""

def _parse_runtime(r):
    if not r: return ""
    try:
        if r.isdigit(): return int(r)
        if m := re.search(r'(\d+)\s*(分|分钟|min)', r): return int(m.group(1))
        parts = r.split(':')
        if len(parts) == 3: return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 2: return int(parts[0])
    except: pass
    return ""

def primevideo_extractor(url):
    logging.info("primevideo_extractor is called")
    page, episodes = None, {}
    try:
        page = ini_playwright_page(headless=True, images=False)
        if m := re.search(r'lcl_([a-z]{2}_[A-Z]{2})', url):
            lang_code = m.group(1)
            accept_language = f"{lang_code.replace('_','-')},{lang_code.split('_')[0]};q=0.9"
            page.set_extra_http_headers({"Accept-Language": accept_language})
            logging.info(f"Setting Accept-Language: {accept_language}")
        page.context.clear_cookies()
        page.goto(url, wait_until="networkidle", timeout=60000)
        if (expander := page.locator("a[data-automation-id='ep-expander']")).count() > 0 and (href := expander.get_attribute("href")):
            page.goto(href)
        season_urls = []
        for link in page.locator("a[href*='atv_dp_season_select']").all():
            try:
                if (href := link.get_attribute("href")) and "auth-redirect" not in href and (m := re.search(r's(\d+)', href)):
                    season_urls.append((int(m.group(1)), f"https://www.primevideo.com{href}" if href.startswith('/') else href))
            except: pass
        season_urls = sorted(season_urls, key=lambda x: x[0])
        if season_urls:
            logging.info(f"Found {len(season_urls)} seasons, extracting all seasons")
            for season_num, season_url in season_urls:
                try:
                    page.goto(season_url, wait_until="networkidle", timeout=60000)
                    if (expander := page.locator("a[data-automation-id='ep-expander']")).count() > 0 and (href := expander.get_attribute("href")):
                        page.goto(href)
                    for tid, ed in _extract_episode_data(page).items():
                        if ep := _parse_episode(ed, season_num):
                            episodes[ep.episode_number] = ep
                    logging.info(f"Extracted {len([ep for ep in episodes if ep.startswith(f'S{season_num}E')])} episodes from season {season_num}")
                except Exception as e:
                    logging.warning(f"Failed to extract season {season_num}: {e}", exc_info=True)
        else:
            for tid, ed in _extract_episode_data(page).items():
                if ep := _parse_episode(ed):
                    episodes[ep.episode_number] = ep
        logging.info(f"Successfully extracted {len(episodes)} episodes")
    except Exception as e:
        logging.error(f"Failed to extract Prime Video data: {e}", exc_info=True)
        return {}
    finally:
        if page: cleanup_playwright_page(page)
    return episodes