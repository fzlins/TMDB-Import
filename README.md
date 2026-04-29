# TMDB-Import

[![English](https://img.shields.io/badge/docs-English-blue)](./README.md) [![简体中文](https://img.shields.io/badge/docs-简体中文-yellow)](./docs/README.zh-CN.md) [![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/fzlins/TMDB-Import)

This script uses the Playwright automation framework and only supports Chrome/Chromium browsers. Playwright automatically downloads and manages browsers, eliminating the need for manual driver installation.

# Installation

## Install Dependencies

### Option 1: Install from requirements.txt (Recommended)
```bash
pip install -r requirements.txt
playwright install chromium
```

### Option 2: Install packages individually
```bash
pip install playwright
pip install python-dateutil
pip install Pillow
pip install bordercrop
playwright install chromium
```

# Usage

## Command Line Options
- `-h, --help`: Show help information
- `-V, --version`: Show version information  
- `-d, --debug`: Enable debug logging (default is INFO level)
- `--headless`: Run browser in headless mode (default is GUI mode)

## Basic Usage
```
python -m tmdb-import [options] "URL"
```

## Browser Mode Description
- **GUI Mode (default)**: Browser window is visible, suitable for debugging and scenarios requiring manual interaction
- **Headless Mode (--headless)**: Browser runs in the background without displaying a window, suitable for automation scripts and server environments
- Headless mode can improve performance and reduce resource usage, especially suitable for batch processing tasks

### Extract Episode Data
```
python -m tmdb-import "http://www.***.com/video.html"
python -m tmdb-import -d "http://www.***.com/video.html"  # Enable debug logging
python -m tmdb-import --headless "http://www.***.com/video.html"  # Run in headless mode
python -m tmdb-import -d --headless "http://www.***.com/video.html"  # Debug + headless mode
```
- Extract episode data through web links, including title, plot description, duration, release time (mostly current platform time), and background image links, and generate import.csv file for subsequent import.

### Import Data to TMDB
```
python -m tmdb-import "https://www.themoviedb.org/tv/{tv_id}/season/{season_number}?language={language}"
# Example: python -m tmdb-import "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
# Enable debug: python -m tmdb-import -d "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
# Headless mode: python -m tmdb-import --headless "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
# Combined options: python -m tmdb-import -d --headless "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
```
- Import data from import.csv in the directory to TMDB. When uploading backdrop images, automatically crop black borders and adapt to the aspect ratio required by TMDB. On first run, manual login is required (or set `tmdb_username` and `tmdb_password` in `config.ini` for automatic login). See [Configuration](#configuration) for more options.

### Image Processing
```
python -m tmdb-import backdrop "https://www.***.com/image.jpg"
python -m tmdb-import --headless backdrop "https://www.***.com/image.jpg"  # Process backdrop in headless mode
```
- Crop backdrop images to fit TMDB requirements

```
python -m tmdb-import poster "https://www.***.com/image.jpg"
python -m tmdb-import --headless poster "https://www.***.com/image.jpg"  # Process poster in headless mode
```
- Crop poster images to fit TMDB requirements

```
python -m tmdb-import fitsize width*height "https://www.***.com/image.jpg"
python -m tmdb-import --headless fitsize 1920*1080 "https://www.***.com/image.jpg"  # Crop in headless mode
```
- Crop images according to specified width and height

# Configuration

The `config.ini` file in the working directory controls the behaviour of the script. All settings are placed under the `[DEFAULT]` section.

| Key | Default | Description |
| :-- | :-----: | :---------- |
| `encoding` | `utf-8-sig` | CSV file encoding (e.g. `utf-8`, `utf-8-sig`, `gbk`) |
| `save_user_profile` | `true` | Persist the browser session under the `Browser/` folder so you stay logged in between runs |
| `tmdb_username` | *(empty)* | TMDB account username for automatic login |
| `tmdb_password` | *(empty)* | TMDB account password for automatic login |
| `backdrop_forced_upload` | `false` | When `true`, upload a backdrop image even if one already exists on TMDB |
| `backdrop_vote_after_upload` | `false` | When `true`, automatically cast a thumbs-up vote on the newly uploaded backdrop |
| `filter_words` | *(empty)* | Comma-separated words; episodes whose titles contain any of these words are excluded from the CSV (e.g. `番外,加更`) |
| `rename_csv_on_import` | `false` | When `true`, rename `import.csv` to `import_{tmdb_id}_s{season}_{language}.csv` before importing |
| `delete_csv_after_import` | `false` | When `true`, delete the CSV file after a successful import |

Example `config.ini`:
```ini
[DEFAULT]
encoding = utf-8-sig
save_user_profile = true
tmdb_username = your_username
tmdb_password = your_password
backdrop_forced_upload = false
backdrop_vote_after_upload = false
filter_words = 番外,加更
rename_csv_on_import = false
delete_csv_after_import = false
```

# Test Environment
Windows 11, Chrome/Chromium, Python 3, and Visual Studio Code.

# Supported Sites
| Website | Title | Plot | Duration | Release Date | Backdrop | Default Language |
| :-----| :----: | :----: | :----: | :----: | :----: | :----- |
| [anidb](https://anidb.net) | &#10004; | x | &#10004; | &#10004; | x | Follow site |
| [apple](https://tv.apple.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| [asahi](https://tv-asahi.co.jp) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ja-JP |
| [bilibili](https://www.bilibili.com) | &#10004; | x | &#10004; | &#10004; | &#10004; | zh-CN |
| [crunchyroll](https://www.crunchyroll.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | Follow site |
| [cctv](https://tv.cctv.com) | &#10004; | &#10004; | &#10004; | x | &#10004; | zh-CN |
| [disney+](https://www.disneyplus.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| [fod](https://fod.fujitv.co.jp) | &#10004; | &#10004; | x | &#10004; | &#10004; | ja-JP |
| [hbomax](https://www.hbomax.com) | &#10004; | &#10004; | x | &#10004; | &#10004; | Follow site |
| [iqiyi](https://www.iqiyi.com) | &#10004; | x | x | x | &#10004; | zh-CN |
| [ixigua](https://www.ixigua.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| [kktv](https://kktv.me) | &#10004; | x | &#10004; | &#10004; | &#10004; | zh-TW |
| [linetv](https://www.linetv.tw) | &#10004; | x | &#10004; | x | &#10004; | zh-TW |
| [litv](https://www.litv.tv) | &#10004; | x | x | x | &#10004; | zh-TW |
| [mgtv](https://www.mgtv.com) | &#10004; | x | &#10004; | &#10004; | x | zh-CN |
| [mytvsuper](https://www.mytvsuper.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-TW |
| [myvideo](https://www.myvideo.net.tw) | &#10004; |  &#10004; | x | x | &#10004; | zh-TW |
| [netflix](https://www.netflix.com) | &#10004; | &#10004; | x | x | x | Follow site |
| [nhk](https://www.nhk.or.jp) | &#10004; | &#10004; | &#10004; | x | &#10004; | ja-JP |
| [paravi](https://paravi.jp) | &#10004; | &#10004; | x | &#10004; | &#10004; | ja-JP |
| [primevideo](https://www.primevideo.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | Follow site |
| [qq](https://v.qq.com) | &#10004; | x | &#10004; | &#10004; | &#10004; | zh-CN |
| [sohu](https://tv.sohu.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| [tvdb](https://www.thetvdb.com) | &#10004; | x | &#10004; | &#10004; | x | Follow site |
| [tvbanywhere](https://www.tvbanywhere.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-HK |
| [viki](https://www.viki.com) | x | &#10004; | &#10004; | x | &#10004; | en-US |
| [viu](https://www.viu.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| [yahoo](https://tv.yahoo.co.jp) | &#10004; | &#10004; | &#10004; | x | x | Follow site |
| [wavve](https://www.wavve.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ko-KR |
| [youku](https://www.youku.com) | x | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
