# TMDB-Import
脚本仅支持edge和Chrome。将浏览器更新的最新版本，再到Selenium官网下载对应浏览器版本的驱动，解压后将exe文件放到目录下。
下载地址：https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/  
Edge为默认的脚本浏览器。如果想使用Chrome运行脚本，在config.ini文件中，将browser的值改为chrome。

# Required packages
```
pip install selenium
pip install python-dateutil
pip install Pillow
pip install bordercrop
```

# 说明
```
python -m tmdb-import "http://www.***.com/video.html"
```
- 通过网页链接来抓取剧集数据，包括标题、剧情介绍、时长、发布时间（大多数为当前平台的时间）和背景图链接，并生成import.csv文件用于之后的导入。
```
python -m tmdb-import "https://www.themoviedb.org/tv/{tv_id}/season/{season_number}?language={language}"
# ex: -m tmdb-import "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
```
- 导入目录下的import.csv的数据到TMDB。上传背景图时，自动切除黑边和适配TMDB所要求的1.78比例。第一次运行需要在登陆界面手动登陆（或者在代码中填写实现自动登陆），forced_upload（值为True时，在允许在TMDB已有背景图片的情况下继续上传）
```
python -m tmdb-import backdrop "https://www.***.com/image.jpg"
```
- 裁剪出适配TMDB的背景图
```
python -m tmdb-import poster "https://www.***.com/image.jpg"
```
- 裁剪出适配TMDB的海报图片
```
python -m tmdb-import fitsize width*heigh "https://www.***.com/image.jpg"
```
- 按给出的长宽裁剪图片

# 测试环境
Window11、Edge、Python3和Vistual Studio Code。

# 已支持
| 网站 | 标题 | 剧情介绍 | 时长 | 发布时间 | 背景图 | 默认语言 |
| :-----| :----: | :----: | :----: | :----: | :----: | :----- |
| anidb | &#10004; | x | &#10004; | &#10004; | x | 跟随网站 |
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
| myvideo | &#10004; | x | x | x | &#10004; | zh-TW |
| netflix | &#10004; | &#10004; | x | &#10004; | x | 跟随网站 |
| nhk | &#10004; | &#10004; | &#10004; | x | &#10004; | ja-JP |
| paravi | &#10004; | &#10004; | x | &#10004; | &#10004; | ja-JP |
| primevideo | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | 跟随网站 |
| qq | &#10004; | x | &#10004; | &#10004; | x | zh-CN |
| sohu | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| tvdb | &#10004; | x | &#10004; | &#10004; | x | 跟随网站 |
| viki | x | &#10004; | &#10004; | x | &#10004; | en-US |
| viu | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| yahoo | &#10004; | &#10004; | &#10004; | x | x | 跟随网站 |
| wavve | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ko-KR |
| youku | x | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
