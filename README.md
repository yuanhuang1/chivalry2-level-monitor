Chivalry 2 玩家等级更新监控工具 / Chivalry 2 Player Level Monitor   
\n功能简介 / Overview   
\n本项目用于 监控 Chivalry 2 玩家的等级（Level）变化。 通过定时抓取玩家当前等级并与历史快照比对，自动生成变化报告，方便战队或好友圈快速了解谁升级了。 This tool monitors Chivalry 2 player level updates. It fetches current levels periodically, compares them with previous snapshots, and automatically generates change reports, making it easy for clans or friend groups to see who has leveled up.  
\n核心用途 / Key Features:   
\n
\n持续追踪指定玩家的等级提升情况 Continuously track level progression of specified players   
\n
\n生成带时间戳的等级变化报告（存放在 report/ 目录） Generate timestamped level change reports (stored in report/)   
\n
\n保存每次抓取的快照数据（存放在 snapshot/ 目录）作为后续比对的基准 Save snapshot data from each run (stored in snapshot/) as baseline for future comparison   
\n
\n提供轻量 Web UI（基于 Flask），可在局域网内直观查看所有报告与快照 Provide a lightweight Web UI (Flask-based) for viewing reports and snapshots in LAN   
\n
\n支持自定义查询间隔、端口等参数 Customizable query interval, port, and other settings   
\n
\n玩家等级 ≥1000 时自动记为满级，并不再查询，减少无效请求 Automatically cap level display at 1000 for players reaching this level, avoiding unnecessary queries   
\n注意：本工具仅关注 等级数值，不记录比赛胜负、击杀等详细战绩。 Note: This tool tracks only level values, not match results, kills, or other detailed stats.   
\n项目结构 / Project Structure   
\n.   
\n├── check_script.py      等级抓取与报告生成主程序 / Main script for fetching levels & generating reports  
\n├── webui.py             局域网网页查看界面 / LAN web viewer interface  
\n├── config.ini           配置文件（端口、间隔、目录等） / Configuration file (port, interval, directories, etc.)  
\n├── players.txt          初始玩家数据（昵称,等级,玩家ID） / Initial player data (nickname,level,playerID)  
\n├── report/              生成的等级变化报告存放目录 / Directory for generated reports  
\n└── snapshot/            每次运行后保存的玩家快照数据目录 / Directory for snapshot data  
\n  
\n使用方法 / Usage   
\n
\n克隆或下载项目 / Clone or Download 将项目代码保存到本地，例如： Clone or download the project to local, e.g.:  git clone https://github.com/你的用户名/chivalry2-level-monitor.git cd chivalry2-level-monitor  
\n
\n安装依赖 / Install Dependencies 确保安装以下 Python 库： Make sure the following Python libraries are installed:  pip install requests beautifulsoup4 flask  
\n
\n准备玩家数据  Prepare Player Data 编辑 players.txt，按 昵称,等级,玩家ID 格式一行一个，也可用 | 分隔的单行格式。 Edit players.txt in format nickname,level,playerID per line, or use single-line | separated format. 示例（多行） Example (multi-line):  Alice,10,123456 Bob,15,789012 Charlie,8,345678  示例（单行）/ Example (single-line):  Alice,10,123456|Bob,15,789012|Charlie,8,345678   
\n
\n配置参数  Configure Settings 修改 config.ini 中的参数： Modify parameters in config.ini:  sleep_seconds：每次查询间隔时间（秒）  Interval between queries (seconds) init_player_file：首次运行或找不到快照时的基准玩家数据文件  Baseline player file for first run or if no snapshot exists report_dir、snapshot_dir：输出目录  Output directories webui_port：Web UI 服务监听端口 / Port for Web UI service  
\n
\n运行等级抓取  Run Level Fetcher 执行： Run:   python check_script.py  程序会读取最新快照或初始玩家文件，依次抓取等级，生成报告与新的快照文件。 The program reads the latest snapshot or initial player file, fetches levels one by one, and generates reports & new snapshots. 运行结束后可在 report 与 snapshot/ 目录查看结果。 Check report/ and snapshot/ after execution.  
\n
\n启动网页查看 / Start Web Viewer 执行： Run:   python webui.py  浏览器访问 http://<你的IP>:端口（端口见 config.ini），即可在局域网内查看所有报告与快照列表。 Visit http://<your IP>:<port> (see config.ini) in browser to view all reports and snapshots in LAN.  
\n注意事项 / Notes   
\n
\n需联网访问 https://chivalry2stats.com 抓取数据，请确保网络畅通 Internet access to https://chivalry2stats.com is required for data fetching.   
\n
\n查询间隔不宜设置过短，以免被目标站点限制访问 Do not set query interval too short to avoid being rate-limited.   
\n
\n玩家等级 ≥1000 时会自动记为满级，并不再发起查询请求 Levels ≥1000 are capped and no further queries are sent.   
\n
\nWeb UI 默认只允许局域网访问，如需外网访问请自行配置路由或端口映射 Web UI is LAN-only by default; configure routing/port mapping for external access.   
\n
\n所有生成的报告和快照均为本地文件，请定期备份以防丢失 Reports and snapshots are stored locally; backup regularly to prevent loss.   
\n适用场景 / Use Cases   
\n
\n战队每日等级变化追踪 / Daily level tracking for clans   
\n
\n好友间互相督促升级 / Friends encouraging each other to level up   
\n
\n长期记录玩家成长曲线（可配合外部工具分析快照数据） / Long-term player growth recording (snapshot data can be analyzed with external tools)   
\n许可证 / License   
\n本项目采用 MIT 许可证，可自由使用、修改与分发。 This project is licensed under the MIT License, free to use, modify and distribute.