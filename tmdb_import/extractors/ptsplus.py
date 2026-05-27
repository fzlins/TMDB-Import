import json
import logging
import re
import urllib.request
from urllib.parse import urlparse

from ..common import Episode, Metadata, Season

# ex: https://www.ptsplus.tv/zh/programs/2758c4b8-8e25-4d10-8dae-2d0978345c98
# ex: https://www.ptsplus.tv/zh/programs/2758c4b8-8e25-4d10-8dae-2d0978345c98/seasons/90c4215b-b771-45f0-a1f1-fa506747da35
# backdrop: 1920x1080

GRAPHQL_URL = "https://www.ptsplus.tv/graphql"

PROGRAM_QUERY = """
query GetProgram($programId: ID!) {
  program(id: $programId) {
    id
    name
    introduction
    latestCover
    bannerLOGO
    bannerCover
    seasonCount
    episodeCount
    seasons {
      id
      name
      number
      releaseYear
      releaseMonth
      introduction
      cover
      bannerCover
      episodes {
        id
        name
        introduction
        cover
        number
        video {
          id
          duration
        }
      }
    }
  }
}
"""


def _graphql_request(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def ptsplus_extractor(url):
    logging.info("ptsplus_extractor is called")

    urlData = urlparse(url)
    urlPath = urlData.path.strip("/")
    path_parts = urlPath.split("/")

    # Extract programId and optional seasonId from URL path.
    # Path format: {locale}/programs/{programId}[/seasons/{seasonId}]
    program_id = None
    season_id = None

    try:
        prog_idx = path_parts.index("programs")
        program_id = path_parts[prog_idx + 1]
    except (ValueError, IndexError):
        logging.error(f"Could not extract program ID from URL: {url}")
        return Metadata(url=url, seasons=[])

    try:
        season_idx = path_parts.index("seasons")
        season_id = path_parts[season_idx + 1]
    except (ValueError, IndexError):
        pass

    logging.info(f"Program ID: {program_id}, Season ID: {season_id}")

    data = _graphql_request(PROGRAM_QUERY, {"programId": program_id})

    if "errors" in data:
        logging.error(f"GraphQL errors: {data['errors']}")
        return Metadata(url=url, seasons=[])

    program = data["data"]["program"]
    program_name = program["name"]
    logging.info(f"Program: {program_name}")
    logging.info(f"backdrop: {program.get('latestCover', '')}")
    logging.info(f"LOGO: {program.get('bannerLOGO', '')}")

    all_seasons = program.get("seasons", [])
    if not all_seasons:
        logging.error("No seasons found for this program")
        return Metadata(url=url, seasons=[])

    if season_id:
        # Extract from specific season only
        target_seasons = [s for s in all_seasons if s["id"] == season_id]
        if not target_seasons:
            logging.error(f"Season {season_id} not found in program {program_id}")
            return Metadata(url=url, seasons=[])
    else:
        # Extract all seasons; sort chronologically (API returns newest first,
        # where season.number=1 is most recent, higher number = older).
        target_seasons = sorted(all_seasons, key=lambda s: s.get("number", 0), reverse=True)

    season_list = []

    for season in target_seasons:
        season_number = season.get("number")
        season_name = season.get("name", "")
        logging.info(f"Season: {season_name}")

        season_eps = {}
        fallback_episode_counter = 1

        for ep in season.get("episodes", []):
            ep_number = ep.get("number")
            if ep_number is None:
                ep_number = fallback_episode_counter

            ep_name = re.sub(r'\s*ep\d+$', '', ep.get("name", ""), flags=re.IGNORECASE).strip()
            ep_overview = ep.get("introduction", "")
            ep_backdrop = ep.get("cover", "")

            # Runtime: video.duration is in seconds; convert to minutes
            video = ep.get("video")
            ep_runtime = round(video["duration"] / 60) if video and video.get("duration") else ""

            # Per-episode air date is not exposed by the PTS+ API
            ep_air_date = ""

            season_eps[ep_number] = Episode(
                ep_number,
                ep_name,
                ep_air_date,
                ep_runtime,
                ep_overview,
                ep_backdrop,
            )
            fallback_episode_counter += 1

        season_list.append(
            Season(
                season_number=season_number,
                name=season_name,
                overview=season.get("introduction", ""),
                poster=season.get("cover", ""),
                episodes=season_eps,
            )
        )

    total_episodes = sum(len(s.episodes) for s in season_list)
    logging.info(f"Successfully extracted {total_episodes} episodes")
    return Metadata(url=url, language="zh-TW", name=program_name, seasons=season_list)
