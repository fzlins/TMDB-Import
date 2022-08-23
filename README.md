# TMDB-Import

Install browser drivers：https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/

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
python -m episodes-import
```
- 导入目录下的import.csv文件里的数据到TMDB。上传背景图时，自动切除黑边和适配TMDB所要求的1.78比例。第一次运行需要在登陆界面手动登陆（或者在代码中填写实现自动登陆），tmdbID，seasonID，forced_upload（值为True时，在允许在TMDB已有背景图片的情况下继续上传），thumbs_up(值为True时，给最自己最后上传的图片点赞)

# 环境
Window11、Edge、Python3和Vistual Studio Code。如果使用其它浏览器，则需要把下面定义Edge浏览器的代码修改为所用浏览器。以Chrome为例：
- options = webdriver.EdgeOptions() 改成 options = webdriver.ChromeOptions()
- driver = webdriver.Edge(options=options) 改成 driver = webdriver.Chrome(options=options)

# 已支持
| 网站 | 标题 | 剧情介绍 | 时长 | 发布时间 | 背景图 | 默认语言 |
| :-----| :----: | :----: | :----: | :----: | :----: | :----- |
| bilibili | &#10004; | x | &#10004; | &#10004; | &#10004; | zh-CN |
| cctv4k | x | &#10004; | &#10004; | x | &#10004; | zh-CN |
| disney+ | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| fod | &#10004; | &#10004; | x | &#10004; | &#10004; | ja-JP |
| iqiyi | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| kktv | &#10004; | x | &#10004; | &#10004; | &#10004; | zh-TW |
| mgtv | &#10004; | x | &#10004; | &#10004; | &#10004; | zh-CN |
| netflix | &#10004; | &#10004; | x | &#10004; | x | 跟随网站 |
| nhk | &#10004; | &#10004; | &#10004; | x | &#10004; | ja-JP |
| paravi | &#10004; | &#10004; | x | &#10004; | &#10004; | ja-JP |
| primevideo | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | 跟随网站 |
| qq | x | x | &#10004; | &#10004; | &#10004; | zh-CN |
| viki | x | &#10004; | &#10004; | X | &#10004; | en-US |
| viu | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
| wavve | &#10004; | &#10004; | &#10004; | &#10004; | &#10004; | ko-KR |
| youku | x | &#10004; | &#10004; | &#10004; | &#10004; | zh-CN |
