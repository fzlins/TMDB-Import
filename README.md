# TMDB-Import

Install browser drivers：https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/

# Required packages
pip install selenium

pip install python-dateutil

# 说明
- data_genatory.py：修改url变量里的网页链接来抓取剧集数据（包括标题、内容简介、时长、首播时间和背景图链接），并生成import.csv文件用于之后的导入。
- episodes-import.py：导入import.csv里的数据到TMDB。需要修改账号，密码，tmdbID，seasonID，downloadBackdrop（允许下载背景图片），uploadBackup(选项上传背景图片到TMDB)

测试环境为：Window11、Edge、Python3和Vistual Studio Code。如果使用其它浏览器，则需要把下面定义Edge浏览器的代码修改为所用浏览器。以Chrome为例：
- options = webdriver.EdgeOptions() 改成 options = webdriver.ChromeOptions()
- driver = webdriver.Edge(options=options) 改成 driver = webdriver.Chrome(options=options)
