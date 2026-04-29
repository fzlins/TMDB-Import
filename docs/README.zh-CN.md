# TMDB-Import

[![English](https://img.shields.io/badge/docs-English-blue)](../README.md) [![简体中文](https://img.shields.io/badge/docs-简体中文-yellow)](./README.zh-CN.md) [![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/fzlins/TMDB-Import)

脚本使用 Playwright 自动化框架，仅支持 Chrome/Chromium 浏览器。Playwright 会自动下载和管理浏览器，无需手动安装驱动程序。

# 安装

## 安装依赖包

### 方式一：使用 requirements.txt 安装（推荐）
```bash
pip install -r requirements.txt
playwright install chromium
```

### 方式二：单独安装各个依赖包
```bash
pip install playwright
pip install python-dateutil
pip install Pillow
pip install bordercrop
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

- 导入目录下的 import.csv 的数据到 TMDB。上传背景图时，自动切除黑边并适配 TMDB 所要求的宽高比。第一次运行需要在登陆界面手动登陆，也可在 `config.ini` 中填写 `tmdb_username` 和 `tmdb_password` 实现自动登陆。更多选项请参阅[配置说明](#配置说明)。

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

# 配置说明

工作目录下的 `config.ini` 文件用于控制脚本行为，所有配置项均位于 `[DEFAULT]` 节。

| 配置项 | 默认值 | 说明 |
| :----- | :----: | :--- |
| `encoding` | `utf-8-sig` | CSV 文件编码（如 `utf-8`、`utf-8-sig`、`gbk`） |
| `save_user_profile` | `true` | 将浏览器会话持久化到 `Browser/` 目录，避免每次运行都需要重新登陆 |
| `tmdb_username` | *(留空)* | TMDB 账号用户名，用于自动登陆 |
| `tmdb_password` | *(留空)* | TMDB 账号密码，用于自动登陆 |
| `backdrop_forced_upload` | `false` | 值为 `true` 时，即使 TMDB 已有背景图也强制上传 |
| `backdrop_vote_after_upload` | `false` | 值为 `true` 时，上传背景图后自动点赞 |
| `filter_words` | *(留空)* | 过滤词，多个过滤词用逗号分隔；集名包含过滤词的条目将被排除在 CSV 之外（如 `番外,加更`） |
| `rename_csv_on_import` | `false` | 值为 `true` 时，导入前将 `import.csv` 重命名为 `import_{tmdb_id}_s{season}_{language}.csv` |
| `delete_csv_after_import` | `false` | 值为 `true` 时，导入完成后删除 CSV 文件 |

`config.ini` 示例：
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
| [mytvsuper](https://www.mytvsuper.com)  | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-TW    |
| [myvideo](https://www.myvideo.net.tw)    | &#10004; | &#10004; |    x     |    x     | &#10004; | zh-TW    |
| [netflix](https://www.netflix.com)    | &#10004; | &#10004; |    x     | x |    x     | 跟随网站 |
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
