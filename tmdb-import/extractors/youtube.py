import json
import logging
import urllib.request
from urllib.parse import urlparse, parse_qs
from ..common import Episode

#https://www.youtube.com/playlist?list=PLiC9HIB4b8TpWemiXT26r7Wv2Cg6b74SX 

_API_URL = "https://www.youtube.com/youtubei/v1"
_CLIENT = {
    "clientName": "WEB",
    "clientVersion": "2.20231121.07.00",
    "hl": "en",
    "gl": "US",
}


def _post(endpoint, body):
    url = f"{_API_URL}/{endpoint}?prettyPrint=false"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-YouTube-Client-Name": "1",
            "X-YouTube-Client-Version": _CLIENT["clientVersion"],
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", "ignore"))


def _context():
    return {"client": _CLIENT}


def _get_text(obj):
    if not obj:
        return ""
    if "simpleText" in obj:
        return obj["simpleText"]
    if "runs" in obj:
        return "".join(r.get("text", "") for r in obj["runs"])
    return ""


def _best_thumbnail(thumbnails):
    if not thumbnails:
        return ""
    return max(thumbnails, key=lambda t: t.get("width", 0) * t.get("height", 0)).get("url", "")


def _extract_playlist_video_list(response):
    try:
        tabs = response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        content = tabs[0]["tabRenderer"]["content"]
        sections = content["sectionListRenderer"]["contents"]
        items = sections[0]["itemSectionRenderer"]["contents"]
        return items[0]["playlistVideoListRenderer"]
    except (KeyError, IndexError):
        return None


def _extract_continuation_items(response):
    try:
        actions = response["onResponseReceivedActions"]
        return actions[0]["appendContinuationItemsAction"]["continuationItems"]
    except (KeyError, IndexError):
        return []


def _parse_video_items(items):
    videos = []
    for item in items:
        renderer = item.get("playlistVideoRenderer")
        if not renderer or not renderer.get("isPlayable", True):
            continue
        video_id = renderer.get("videoId", "")
        if not video_id:
            continue
        title = _get_text(renderer.get("title"))
        length_sec = int(renderer.get("lengthSeconds") or 0)
        videos.append({
            "video_id": video_id,
            "title": title,
            "runtime": round(length_sec / 60),
        })
    return videos


def _get_continuation_token(items):
    for item in items:
        cr = item.get("continuationItemRenderer")
        if cr:
            return (
                cr.get("continuationEndpoint", {})
                .get("continuationCommand", {})
                .get("token")
            )
    return None


def youtube_extractor(url):
    logging.info("youtube_extractor is called")

    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query)
    playlist_id = qs.get("list", [None])[0]
    if not playlist_id:
        logging.error("Could not extract playlist ID from URL")
        return {}

    logging.info(f"Playlist ID: {playlist_id}")

    # --- Step 1: Get playlist metadata and first page of videos ---
    response = _post("browse", {
        "context": _context(),
        "browseId": f"VL{playlist_id}",
    })

    header = response.get("header", {})
    plh = header.get("playlistHeaderRenderer", {})
    playlist_name = (
        _get_text(plh.get("title"))
        or _get_text(header.get("pageHeaderRenderer", {}).get("pageTitle"))
        or ""
    )
    logging.info(f"Playlist name: {playlist_name}")

    # --- Step 2: Collect all videos across pages ---
    all_videos = []
    pvl = _extract_playlist_video_list(response)
    if pvl:
        items = pvl.get("contents", [])
        all_videos.extend(_parse_video_items(items))
        token = _get_continuation_token(items)
        while token:
            cont_response = _post("browse", {
                "context": _context(),
                "continuation": token,
            })
            cont_items = _extract_continuation_items(cont_response)
            all_videos.extend(_parse_video_items(cont_items))
            token = _get_continuation_token(cont_items)

    logging.info(f"Total videos collected: {len(all_videos)}")

    # --- Step 3: Fetch upload date and description per video via player API ---
    episodes = {}
    for ep_num, video in enumerate(all_videos, start=1):
        video_id = video["video_id"]
        air_date = ""
        overview = ""
        thumbnail = ""
        try:
            player = _post("player", {
                "context": _context(),
                "videoId": video_id,
            })
            publish_date = (
                player.get("microformat", {})
                .get("playerMicroformatRenderer", {})
                .get("publishDate", "")
            )
            air_date = publish_date[:10] if publish_date else ""
            overview = player.get("videoDetails", {}).get("shortDescription", "")
            thumbnails = (
                player.get("videoDetails", {})
                .get("thumbnail", {})
                .get("thumbnails", [])
            )
            thumbnail = _best_thumbnail(thumbnails)
        except Exception as e:
            logging.warning(f"Could not fetch details for {video_id}: {e}")

        # Fallback: construct maxresdefault URL directly
        if not thumbnail:
            thumbnail = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

        episodes[ep_num] = Episode(
            ep_num,
            video["title"],
            air_date,
            video["runtime"],
            overview,
            thumbnail,
        )
        logging.info(f"[{ep_num}] {video['title']} ({video['runtime']} min, {air_date})")

    logging.info(f"Extracted {len(episodes)} episodes from playlist '{playlist_name}'")
    return episodes
