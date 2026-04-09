Chivalry 2 等级检查工具（GUI版）  

一个基于 Python Tkinter 的小工具，用于批量查询 Chivalry 2 玩家的等级变化，支持缓存、快照、报告生成，并通过图形界面方便操作。  

功能特点  
读取玩家列表（支持 CSV 或 | 分隔）  
调用 chivalry2stats.com 查询玩家等级  
自动缓存查询结果（12 小时有效），减少重复请求  
满级（大于等于1000）玩家自动跳过  
生成带时间戳的等级变化报告（TXT）  
保存每次查询的玩家等级快照，供下次对比  
一键清理缓存  
多线程执行，GUI 界面不卡顿  
跨平台（Windows  macOS  Linux）  

项目结构  
chivalry_gui_project 文件夹下包含  
chivalry_gui.py  主程序（GUI + 业务逻辑）  
players.txt  初始玩家列表（昵称,等级,玩家ID）  
cache.json  缓存文件（自动生成）  
report  报告目录（自动生成），里面的文件名为 report_年月日_时分秒.txt  
snapshot  快照目录（自动生成），里面的文件名为 players_年月日_时分秒.txt  
README.md  本说明文档  

快速开始  
环境准备  
Python 3.6 或以上  
安装依赖命令  
pip install requests beautifulsoup4  

初始玩家列表  
在项目根目录创建 players.txt，格式如下（每行一个玩家或用 | 分隔）  
玩家A,10,123456  
玩家B,25,234567  
玩家C,999,345678  
也可以用 | 分隔写成一行  
玩家A,10,123456|玩家B,25,234567|玩家C,999,345678  

运行程序  
命令  
python chivalry_gui.py  
会出现 GUI 窗口  
按钮 开始检查  执行等级查询并生成报告和快照  
按钮 清理缓存  删除 cache.json，下次查询将全部重新请求网络  

配置说明  
在 chivalry_gui.py 顶部可修改以下常量  
INIT_PLAYER_FILE  初始玩家列表文件名  默认 players.txt  
REPORT_DIR  报告保存目录  默认 report  
SNAPSHOT_DIR  快照保存目录  默认 snapshot  
CACHE_FILE  缓存文件名  默认 cache.json  
SLEEP_SECONDS  两次网络查询间的等待时间（防封）  默认 10 秒  
CACHE_TTL  缓存有效时长（秒）  默认 43200（12小时）  

报告与快照  
报告文件位于 report 目录，包含本次查询的时间、成功失败变化统计、变化玩家详情（旧等级到新等级）。  
快照文件位于 snapshot 目录，保存当前所有玩家的等级，用作下次运行的基准数据。  
快照文件命名格式为 players_年月日_时分秒.txt，内容为 昵称,等级,玩家ID 用 | 拼接的单行。  

缓存机制  
查询结果会保存在 cache.json，结构示例  
编号123456 对应等级30 和时间戳  
编号234567 对应等级45 和时间戳  
缓存有效期由 CACHE_TTL 控制，过期将重新查询。  
可在 GUI 点击 清理缓存 手动删除。  

注意事项  
网络查询受目标站点响应影响，查询间隔不宜过短，默认 10 秒。  
如果目标网站无法访问或改版，需更新 fetch_level 中的解析逻辑。  
异常信息可能包含换行符，会在 GUI 日志中直接换行显示，属正常现象。  
程序会自动创建 report 与 snapshot 目录。  
请勿频繁大量请求，以免被目标站点封禁 IP。  

许可  
本项目仅供学习与交流使用，请勿用于商业或恶意爬取。
