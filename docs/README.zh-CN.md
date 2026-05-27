# TMDB-Import

[![English](https://img.shields.io/badge/docs-English-blue)](../README.md) [![简体中文](https://img.shields.io/badge/docs-简体中文-yellow)](./README.zh-CN.md) [![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/fzlins/TMDB-Import)

脚本使用 Playwright 自动化框架，仅支持 Chrome/Chromium 浏览器。Playwright 会自动下载和管理浏览器，无需手动安装驱动程序。

# 安装

## 安装依赖包

### 完整安装（所有功能）
```bash
pip install -r requirements.txt
playwright install chromium
```

### 最小化安装（仅核心功能）
```bash
pip install python-dateutil
```
最小化安装支持大部分不需要浏览器自动化的提取器。

### 可选依赖

依赖项按需加载。当某个功能需要缺失的包时，程序会显示友好的错误提示：

- **浏览器自动化**（用于优酷、爱奇艺等需要 JavaScript 渲染的网站）
  ```bash
  pip install playwright
  playwright install chromium
  ```

- **中文简繁转换**（简体 ↔ 繁体）
  ```bash
  pip install opencc-python-reimplemented
  ```
  在 `config.ini` 中设置 `chinese_convert = zh-CN`（或 `zh-TW`、`zh-HK`）启用

- **图片处理**（背景图/海报裁剪和格式转换）
  ```bash
  pip install Pillow bordercrop
  ```

### 单独安装各个依赖包
```bash
pip install playwright
pip install python-dateutil
pip install Pillow
pip install bordercrop
pip install opencc-python-reimplemented
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
python -m tmdb_import [选项] "URL"
```

## 浏览器模式说明

- **GUI 模式（默认）**: 浏览器窗口可见，适合调试和需要手动交互的场景
- **无头模式（--headless）**: 浏览器在后台运行，不显示窗口，适合自动化脚本和服务器环境
- 无头模式可以提高性能并减少资源占用，特别适合批量处理任务

### 抓取剧集数据

```
python -m tmdb_import "http://www.***.com/video.html"
python -m tmdb_import -d "http://www.***.com/video.html"  # 启用调试日志
python -m tmdb_import --headless "http://www.***.com/video.html"  # 无头模式运行
python -m tmdb_import -d --headless "http://www.***.com/video.html"  # 调试+无头模式
python -m tmdb_import "http://www.***.com/video.html" --debug  # 选项也可放在 URL 后
```

- 通过网页链接来抓取剧集数据，包括标题、剧情介绍、时长、发布时间（大多数为当前平台的时间）和背景图链接。
- 输出文件：
	- `metadata.json`：完整结构化元数据（剧集级、季级、集级信息）
	- `import.csv`：用于 TMDB 导入的扁平化剧集列表

### 导入数据到 TMDB

```
python -m tmdb_import "https://www.themoviedb.org/tv/{tv_id}/season/{season_number}?language={language}"
# 示例: python -m tmdb_import "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
# 启用调试: python -m tmdb_import -d "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
# 无头模式: python -m tmdb_import --headless "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
# 组合选项: python -m tmdb_import -d --headless "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
```

- 导入目录下的 import.csv 的数据到 TMDB。上传背景图时，自动切除黑边并适配 TMDB 所要求的宽高比。第一次运行需要在登陆界面手动登陆，也可在 `config.ini` 中填写 `tmdb_username` 和 `tmdb_password` 实现自动登陆。更多选项请参阅[配置说明](#配置说明)。

### 图片处理

```
python -m tmdb_import backdrop "https://www.***.com/image.jpg"
python -m tmdb_import --headless backdrop "https://www.***.com/image.jpg"  # 无头模式处理背景图
```

- 裁剪出适配 TMDB 的背景图

```
python -m tmdb_import poster "https://www.***.com/image.jpg"
python -m tmdb_import --headless poster "https://www.***.com/image.jpg"  # 无头模式处理海报
```

- 裁剪出适配 TMDB 的海报图片

```
python -m tmdb_import fitsize width*height "https://www.***.com/image.jpg"
python -m tmdb_import --headless fitsize 1920*1080 "https://www.***.com/image.jpg"  # 无头模式裁剪
```

- 按给出的长宽裁剪图片

## 作为 Python 库使用

TMDB-Import 也可以作为 Python 库在您的项目中使用：

```python
# 添加到 sys.path（如果未通过 pip 安装）
import sys
sys.path.insert(0, r'/path/to/TMDB-Import')

# 直接导入（包现在使用下划线）
from tmdb_import import extract_from_url, save_metadata_json, create_csv

# 提取元数据
metadata = extract_from_url("https://tver.jp/series/...")

# 访问元数据
print(metadata.name)        # 剧集名称
print(metadata.overview)    # 剧集简介
print(metadata.poster)      # 海报 URL
print(metadata.language)    # 语言代码（如 'ja-JP'）

# 访问剧集信息
for season in metadata.seasons:
    for episode_num, episode in season.episodes.items():
        print(f"第{episode_num}集: {episode.name}")

# 可选：手动保存文件
save_metadata_json("output.json", metadata)
for season in metadata.seasons:
    if season.episodes:
        create_csv("output.csv", season.episodes)
        break
```

**可用函数：**
- `extract_from_url(url, language="zh-CN")`：从 URL 提取和处理元数据
- `save_metadata_json(filename, metadata)`：将元数据保存为 JSON 文件
- `create_csv(filename, episodes_dict)`：将剧集保存为 CSV 文件

**元数据结构：**
- `Metadata`：剧集级数据（name, overview, poster, backdrop, logo, language, seasons）
- `Season`：季级数据（season_number, name, overview, poster, episodes）
- `Episode`：集级数据（episode_number, name, air_date, runtime, overview, backdrop）

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
| `filter_words` | *(留空)* | 过滤词，多个过滤词用逗号分隔；集名包含过滤词的集将被过滤。剩余集会自动重新编号，但保留原有缺集（例如，若原始有 1,2,3,4,5,6,10 集，过滤掉 2,4 后，结果为 1,2,3,8，保留第 6 集后的缺集） |
| `rename_csv_on_import` | `false` | 值为 `true` 时，导入前将 `import.csv` 重命名为 `import_{tmdb_id}_s{season}_{language}.csv` |
| `delete_csv_after_import` | `false` | 值为 `true` 时，导入完成后删除 CSV 文件 |
| `chinese_convert` | *(留空)* | 抓取后对中文文本进行字体转换。留空则不转换。可选值：`zh-CN`（大陆简体）、`zh-TW`（台湾繁体）、`zh-HK`（香港繁体）。仅当来源语言为中文（`zh-*`）时生效。 |

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
chinese_convert = 
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
| [bilibili.tv](https://www.bilibili.tv) | &#10004; |    x     |    x     | &#10004; | &#10004; | 跟随网站 |
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
| [mytvsuper](https://www.mytvsuper.com)  | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-HK    |
| [myvideo](https://www.myvideo.net.tw)    | &#10004; | &#10004; |    x     |    x     | &#10004; | zh-TW    |
| [netflix](https://www.netflix.com)    | &#10004; | &#10004; |    x     | x |    x     | 跟随网站 |
| [nhk](https://www.nhk.or.jp)        | &#10004; | &#10004; | &#10004; |    x     | &#10004; | ja-JP    |
| [paravi](https://paravi.jp)     | &#10004; | &#10004; |    x     | &#10004; | &#10004; | ja-JP    |
| [primevideo](https://www.primevideo.com) | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | 跟随网站 |
| [ptsplus](https://www.ptsplus.tv)    | &#10004; | &#10004; | &#10004; |    x     | &#10004; | zh-TW    |
| [qq](https://v.qq.com)         | &#10004; |    x     | &#10004; | &#10004; | &#10004; | zh-CN    |
| [sohu](https://tv.sohu.com)       | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN    |
| [tvdb](https://www.thetvdb.com)       | &#10004; |    x     | &#10004; | &#10004; |    x     | 跟随网站 |
| [tvbanywhere](https://www.tvbanywhere.com)| &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-HK    |
| [tver](https://tver.jp)        | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ja-JP    |
| [viki](https://www.viki.com)       |    x     | &#10004; | &#10004; |    x     | &#10004; | en-US    |
| [viu](https://www.viu.com)        | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN    |
| [yahoo](https://tv.yahoo.co.jp)      | &#10004; | &#10004; | &#10004; |    x     |    x     | 跟随网站 |
| [wavve](https://www.wavve.com)      | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ko-KR    |
| [youku](https://www.youku.com)      | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN    |
| [youtube](https://www.youtube.com)  | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | 跟随网站 |
