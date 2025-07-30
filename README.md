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
| anidb | &#10004; | x | &#10004; | &#10004; | x | Follow site |
| apple | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| asahi | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ja-JP |
| bilibili | &#10004; | x | &#10004; | &#10004; | &#10004; | zh-CN |
| cctv | &#10004; | &#10004; | &#10004; | x | &#10004; | zh-CN |
| disney+ | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| fod | &#10004; | &#10004; | x | &#10004; | &#10004; | ja-JP |
| iqiyi | &#10004; | x | x | x | &#10004; | zh-CN |
| ixigua | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| kktv | &#10004; | x | &#10004; | &#10004; | &#10004; | zh-TW |
| mgtv | &#10004; | x | &#10004; | &#10004; | x | zh-CN |
| mgtv | &#10004; | x | x | x | x | zh-TW |
| mytvsuper | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-TW |
| myvideo | &#10004; |  &#10004; | x | x | &#10004; | zh-TW |
| netflix | &#10004; | &#10004; | x | &#10004; | x | Follow site |
| nhk | &#10004; | &#10004; | &#10004; | x | &#10004; | ja-JP |
| paravi | &#10004; | &#10004; | x | &#10004; | &#10004; | ja-JP |
| primevideo | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | Follow site |
| qq | &#10004; | x | &#10004; | &#10004; | x | zh-CN |
| sohu | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| tvdb | &#10004; | x | &#10004; | &#10004; | x | Follow site |
| viki | x | &#10004; | &#10004; | x | &#10004; | en-US |
| viu | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| yahoo | &#10004; | &#10004; | &#10004; | x | x | Follow site |
| wavve | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ko-KR |
| youku | x | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
