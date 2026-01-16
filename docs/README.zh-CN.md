# TMDB-Import

[![English](https://img.shields.io/badge/docs-English-blue)](../README.md) [![简体中文](https://img.shields.io/badge/docs-简体中文-yellow)](./README.zh-CN.md)

脚本使用 Playwright 自动化框架，仅支持 Chrome/Chromium 浏览器。Playwright 会自动下载和管理浏览器，无需手动安装驱动程序。

# 所需依赖包

```
pip install playwright
pip install python-dateutil
pip install Pillow
pip install bordercrop
```

安装 Playwright 浏览器：

```
playwright install chromium
```

# 使用说明

## 命令行选项

- `-h, --help`: 显示帮助信息
- `-V, --version`: 显示版本信息
- `-d, --debug`: 启用调试日志（默认为 INFO 级别）
- `--headless`: 以无头模式运行浏览器（默认为 GUI 模式）

## 基本用法

```
python -m tmdb-import [选项] "URL"
```

## 浏览器模式说明

- **GUI 模式（默认）**: 浏览器窗口可见，适合调试和需要手动交互的场景
- **无头模式（--headless）**: 浏览器在后台运行，不显示窗口，适合自动化脚本和服务器环境
- 无头模式可以提高性能并减少资源占用，特别适合批量处理任务

### 抓取剧集数据

```
python -m tmdb-import "http://www.***.com/video.html"
python -m tmdb-import -d "http://www.***.com/video.html"  # 启用调试日志
python -m tmdb-import --headless "http://www.***.com/video.html"  # 无头模式运行
python -m tmdb-import -d --headless "http://www.***.com/video.html"  # 调试+无头模式
```

- 通过网页链接来抓取剧集数据，包括标题、剧情介绍、时长、发布时间（大多数为当前平台的时间）和背景图链接，并生成 import.csv 文件用于之后的导入。

### 导入数据到 TMDB

```
python -m tmdb-import "https://www.themoviedb.org/tv/{tv_id}/season/{season_number}?language={language}"
# 示例: python -m tmdb-import "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
# 启用调试: python -m tmdb-import -d "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
# 无头模式: python -m tmdb-import --headless "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
# 组合选项: python -m tmdb-import -d --headless "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
```

- 导入目录下的 import.csv 的数据到 TMDB。上传背景图时，自动切除黑边和适配 TMDB 所要求的 1.78 比例。第一次运行需要在登陆界面手动登陆（或者在代码中填写实现自动登陆），forced_upload（值为 True 时，在允许在 TMDB 已有背景图片的情况下继续上传）

### 图片处理

```
python -m tmdb-import backdrop "https://www.***.com/image.jpg"
python -m tmdb-import --headless backdrop "https://www.***.com/image.jpg"  # 无头模式处理背景图
```

- 裁剪出适配 TMDB 的背景图

```
python -m tmdb-import poster "https://www.***.com/image.jpg"
python -m tmdb-import --headless poster "https://www.***.com/image.jpg"  # 无头模式处理海报
```

- 裁剪出适配 TMDB 的海报图片

```
python -m tmdb-import fitsize width*height "https://www.***.com/image.jpg"
python -m tmdb-import --headless fitsize 1920*1080 "https://www.***.com/image.jpg"  # 无头模式裁剪
```

- 按给出的长宽裁剪图片

# 测试环境

Windows 11、Chrome/Chromium、Python 3 和 Visual Studio Code。

# 已支持

| 网站       |   标题   | 剧情介绍 |   时长   | 发布时间 |  背景图  | 默认语言 |
| :--------- | :------: | :------: | :------: | :------: | :------: | :------- |
| [anidb](https://anidb.net)      | &#10004; |    x     | &#10004; | &#10004; |    x     | 跟随网站 |
| [apple](https://tv.apple.com)      | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN    |
| [asahi](https://tv-asahi.co.jp)      | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ja-JP    |
| [bilibili](https://www.bilibili.com)   | &#10004; |    x     | &#10004; | &#10004; | &#10004; | zh-CN    |
| [crunchyroll](https://www.crunchyroll.com)| &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | 跟随网站 |
| [cctv](https://tv.cctv.com)       | &#10004; | &#10004; | &#10004; |    x     | &#10004; | zh-CN    |
| [disney+](https://www.disneyplus.com)    | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN    |
| [fod](https://fod.fujitv.co.jp)        | &#10004; | &#10004; |    x     | &#10004; | &#10004; | ja-JP    |
| [hbomax](https://www.hbomax.com)     | &#10004; | &#10004; |    x     | &#10004; | &#10004; | 跟随网站 |
| [iqiyi](https://www.iqiyi.com)      | &#10004; |    x     |    x     |    x     | &#10004; | zh-CN    |
| [ixigua](https://www.ixigua.com)     | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN    |
| [kktv](https://kktv.me)       | &#10004; |    x     | &#10004; | &#10004; | &#10004; | zh-TW    |
| [linetv](https://www.linetv.tw)     | &#10004; |    x     | &#10004; |    x     | &#10004; | zh-TW    |
| [litv](https://www.litv.tv)       | &#10004; |    x     |    x     |    x     | &#10004; | zh-TW    |
| [mgtv](https://www.mgtv.com)       | &#10004; |    x     | &#10004; | &#10004; |    x     | zh-CN    |
| [mgtv](https://www.mgtv.com)       | &#10004; |    x     |    x     |    x     |    x     | zh-TW    |
| [mytvsuper](https://www.mytvsuper.com)  | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-TW    |
| [myvideo](https://www.myvideo.net.tw)    | &#10004; | &#10004; |    x     |    x     | &#10004; | zh-TW    |
| [netflix](https://www.netflix.com)    | &#10004; | &#10004; |    x     | &#10004; |    x     | 跟随网站 |
| [nhk](https://www.nhk.or.jp)        | &#10004; | &#10004; | &#10004; |    x     | &#10004; | ja-JP    |
| [paravi](https://paravi.jp)     | &#10004; | &#10004; |    x     | &#10004; | &#10004; | ja-JP    |
| [primevideo](https://www.primevideo.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | 跟随网站 |
| [qq](https://v.qq.com)         | &#10004; |    x     | &#10004; | &#10004; | &#10004; | zh-CN    |
| [sohu](https://tv.sohu.com)       | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN    |
| [tvdb](https://www.thetvdb.com)       | &#10004; |    x     | &#10004; | &#10004; |    x     | 跟随网站 |
| [tvbanywhere](https://www.tvbanywhere.com)| &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-HK    |
| [viki](https://www.viki.com)       |    x     | &#10004; | &#10004; |    x     | &#10004; | en-US    |
| [viu](https://www.viu.com)        | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN    |
| [yahoo](https://tv.yahoo.co.jp)      | &#10004; | &#10004; | &#10004; |    x     |    x     | 跟随网站 |
| [wavve](https://www.wavve.com)      | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ko-KR    |
| [youku](https://www.youku.com)      |    x     | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN    |
