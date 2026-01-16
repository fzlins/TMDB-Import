# TMDB-Import

[![English](https://img.shields.io/badge/docs-English-blue)](./README.md) [![简体中文](https://img.shields.io/badge/docs-简体中文-yellow)](./docs/README.zh-CN.md)

This script uses the Playwright automation framework and only supports Chrome/Chromium browsers. Playwright automatically downloads and manages browsers, eliminating the need for manual driver installation.

# Required Packages
```
pip install playwright
pip install python-dateutil
pip install Pillow
pip install bordercrop
```

Install Playwright browser:
```
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
- Import data from import.csv in the directory to TMDB. When uploading background images, automatically crop black borders and adapt to the 1.78 ratio required by TMDB. First run requires manual login at the login interface (or fill in code to implement automatic login), forced_upload (when set to True, allows continued upload when TMDB already has background images)

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
| [netflix](https://www.netflix.com) | &#10004; | &#10004; | x | &#10004; | x | Follow site |
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
