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
- 运行data_genatory.py：修改url变量里的网页链接来抓取剧集数据，包括标题、剧情介绍、时长、发布时间（大多数为当前平台的时间）和背景图链接，并生成import.csv文件用于之后的导入。
- 运行episodes-import.py：导入目录下的import.csv文件里的数据到TMDB。上传背景图时，自动切除黑边和适配TMDB所要求的1.78比例。第一次运行需要在登陆界面手动登陆（或者在代码中填写实现自动登陆），tmdbID，seasonID，forced_upload（值为True时，在允许在TMDB已有背景图片的情况下继续上传），thumbs_up(值为True时，给最自己最后上传的图片点赞)

# 已支持
## zh-CN
- iqiyi：标题、剧情介绍、时长、发布时间和背景图
- youku：剧情介绍、时长、发布时间和背景图
- qq：时长、发布时间和背景图
- mgtv: 标题、时长、发布时间和背景图
- disney+：标题、剧情介绍、时长、发布时间和背景图
- bilibili：标题、时长、发布时间和背景图

## zh-TW
- KKTV：标题、时长、发布时间和背景图

## en-US
- viki：剧情介绍、时长、发布时间和背景图

## ja-JP
- paravi.jp：标题、剧情介绍、发布时间和背景图
- nhk：标题、剧情介绍、发布时间和背景图
- fod：标题、剧情介绍、时长和背景图

## ko-KR
- wavve：标题、剧情介绍、发布时间和背景图

## 多语言
- amazon：标题、剧情介绍、时长、发布时间和背景图

# 环境
Window11、Edge、Python3和Vistual Studio Code。如果使用其它浏览器，则需要把下面定义Edge浏览器的代码修改为所用浏览器。以Chrome为例：
- options = webdriver.EdgeOptions() 改成 options = webdriver.ChromeOptions()
- driver = webdriver.Edge(options=options) 改成 driver = webdriver.Chrome(options=options)
