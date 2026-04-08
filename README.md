Chivalry 2 玩家等级更新监控工具

功能简介  
本项目用于监控 Chivalry 2 玩家的等级变化。  
通过定时抓取玩家当前等级并与历史快照比对，自动生成变化报告，方便战队或好友圈快速了解谁升级了。  

注意：本工具仅关注等级数值，不记录比赛胜负、击杀等详细战绩。

核心特性  
持续追踪指定玩家的等级提升情况  
生成带时间戳的等级变化报告（存放在 report/ 目录）  
保存每次抓取的快照数据（存放在 snapshot/ 目录）作为后续比对的基准  
提供轻量 Web UI（基于 Flask），可在局域网内直观查看所有报告与快照  
支持自定义查询间隔、端口等参数  
玩家等级达到 1000 时自动记为满级，并不再查询，减少无效请求

项目结构  
.  
├── check_script.py      等级抓取与报告生成主程序  
├── webui.py             局域网网页查看界面  
├── config.ini           配置文件（端口、间隔、目录等）  
├── players.txt          初始玩家数据（昵称,等级,玩家ID）  
├── report/              生成的等级变化报告存放目录  
└── snapshot/            每次运行后保存的玩家快照数据目录

使用方法

1. 克隆或下载项目  
将项目代码保存到本地，例如：  
git clone https://github.com/你的用户名/chivalry2-level-monitor.git  
cd chivalry2-level-monitor

2. 安装依赖  
确保安装以下 Python 库：  
pip install requests beautifulsoup4 flask

3. 准备玩家数据  
编辑 players.txt，按 昵称,等级,玩家ID 格式一行一个，也可用 | 分隔的单行格式。  

示例（多行）：  
Alice,10,123456  
Bob,15,789012  
Charlie,8,345678  

示例（单行）：  
Alice,10,123456|Bob,15,789012|Charlie,8,345678

4. 配置参数  
修改 config.ini 中的参数：  
sleep_seconds：每次查询间隔时间（秒）  
init_player_file：首次运行或找不到快照时的基准玩家数据文件  
report_dir、snapshot_dir：输出目录  
webui_port：Web UI 服务监听端口

5. 运行等级抓取  
执行：  
python check_script.py  
程序会读取最新快照或初始玩家文件，依次抓取等级，生成报告与新的快照文件。  
运行结束后可在 report/ 与 snapshot/ 目录查看结果。

6. 启动网页查看  
执行：  
python webui.py  
浏览器访问 http://<你的IP>:端口（端口见 config.ini），即可在局域网内查看所有报告与快照列表。

注意事项  
需联网访问 https://chivalry2stats.com 抓取数据，请确保网络畅通  
查询间隔不宜设置过短，以免被目标站点限制访问  
玩家等级达到 1000 时会自动记为满级，并不再发起查询请求  
Web UI 默认只允许局域网访问，如需外网访问请自行配置路由或端口映射  
所有生成的报告和快照均为本地文件，请定期备份以防丢失

适用场景  
战队每日等级变化追踪  
好友间互相督促升级  
长期记录玩家成长曲线（可配合外部工具分析快照数据）

许可证  
本项目采用 MIT 许可证，可自由使用、修改与分发。



Chivalry 2 Player Level Update Monitor

Function Overview
This tool is used to monitor the level changes of players in Chivalry 2.  
By periodically fetching the current level of players and comparing it with historical snapshots, it automatically generates change reports, making it easy for clans or friend groups to quickly see who has leveled up.  

Note: This tool only focuses on the level value, and does not record detailed battle results such as match wins/losses or kills.

Core Features
- Continuously track the level progression of specified players  
- Generate timestamped level change reports (stored in the report/ directory)  
- Save the snapshot data fetched each time (stored in the snapshot/ directory) as the baseline for future comparisons  
- Provide a lightweight Web UI (based on Flask) for intuitively viewing all reports and snapshots within the local network  
- Support custom parameters such as query interval and port  
- Automatically mark the level as 1000 for players who reach that level and stop querying to reduce unnecessary requests

Project Structure
.  
├── check_script.py      Main script for fetching levels and generating reports  
├── webui.py             LAN web viewer interface  
├── config.ini           Configuration file (port, interval, directories, etc.)  
├── players.txt          Initial player data (nickname,level,playerID)  
├── report/              Directory for generated level change reports  
└── snapshot/            Directory for player snapshot data saved after each run

Usage

1. Clone or Download the Project  
Save the project code to your local machine, for example:  
git clone https://github.com/your-username/chivalry2-level-monitor.git  
cd chivalry2-level-monitor

2. Install Dependencies  
Make sure the following Python libraries are installed:  
pip install requests beautifulsoup4 flask

3. Prepare Player Data  
Edit players.txt, with one entry per line in the format of nickname,level,playerID, or use a single-line format separated by |.  

Example (multi-line):  
Alice,10,123456  
Bob,15,789012  
Charlie,8,345678  

Example (single-line):  
Alice,10,123456|Bob,15,789012|Charlie,8,345678

4. Configure Parameters  
Modify the parameters in config.ini:  
sleep_seconds: The time interval between each query (in seconds)  
init_player_file: The baseline player data file for the first run or when no snapshot is found  
report_dir, snapshot_dir: Output directories  
webui_port: The port number for the Web UI service

5. Run Level Fetching  
Execute:  
python check_script.py  
The program will read the latest snapshot or the initial player file, fetch levels one by one, and generate reports and new snapshot files.  
After running, you can check the results in the report/ and snapshot/ directories.

6. Start Web Viewer  
Execute:  
python webui.py  
Open your browser and visit http://<your-IP>:<port> (see config.ini) to view all reports and snapshot lists within the local network.

Notes
- You need to access https://chivalry2stats.com via the internet to fetch data. Please ensure your network is stable.  
- Do not set the query interval too short to avoid being rate-limited by the target site.  
- When a player's level reaches 1000, it will be automatically marked as max level and no further queries will be sent.  
- The Web UI is accessible on the local network by default. For external access, you need to configure routing or port forwarding yourself.  
- All generated reports and snapshots are stored locally. Please back them up regularly to prevent data loss.

Use Cases
- Daily level tracking for clans  
- Friends encouraging each other to level up  
- Long-term recording of player growth curves (can be analyzed with external tools using snapshot data)

License
This project is licensed under the MIT License, free to use, modify and distribute.
