import requests
from requests.exceptions import Timeout, ConnectionError
from bs4 import BeautifulSoup
import time
import os
import configparser
from datetime import datetime

# ========== 内置配置加载（自动生成 config.ini） ==========
CONFIG_PATH = 'config.ini'

_default_config = {
    "sleep_seconds": "10",
    "init_player_file": "players.txt",
    "report_dir": "report",
    "snapshot_dir": "snapshot",
    "webui_port": "5000"   # ← 新增
}

def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        # 自动生成带注释的默认 config.ini
        default_content = """[DEFAULT]
; 每次查询玩家等级后的间隔时间（秒），防止请求过快被限制
sleep_seconds = 10

; 首次运行或找不到快照文件时，用作基准的玩家数据文件（格式：昵称,等级,玩家ID）
init_player_file = players.txt

; 生成的等级变化报告存放的目录（脚本会自动创建）
report_dir = report

; 每次运行后保存的玩家快照数据目录（脚本会自动创建，用作下次比对的基准）
snapshot_dir = snapshot

; WebUI 服务监听端口（用于网页查看报告和快照）
webui_port = 5000
"""  # ← 新增注释和默认值
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(default_content)
        print(f"[INFO] 已自动生成默认配置文件: {CONFIG_PATH}")
    
    config.read(CONFIG_PATH, encoding='utf-8')
    cfg = dict(config['DEFAULT'])
    # 保证字段齐全
    _default_config = {
        "sleep_seconds": "10",
        "init_player_file": "players.txt",
        "report_dir": "report",
        "snapshot_dir": "snapshot",
        "webui_port": "5000"   # ← 新增
    }
    for k, v in _default_config.items():
        cfg.setdefault(k, v)
    cfg["sleep_seconds"] = int(cfg["sleep_seconds"])
    return cfg

cfg = load_config()

INIT_PLAYER_FILE = cfg["init_player_file"]
REPORT_DIR = cfg["report_dir"]
SNAPSHOT_DIR = cfg["snapshot_dir"]
SLEEP_SECONDS = cfg["sleep_seconds"]
# ==========================================================

def ensure_dirs():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
    if not os.path.exists(SNAPSHOT_DIR):
        os.makedirs(SNAPSHOT_DIR)

def get_latest_snapshot_file():
    files = [f for f in os.listdir(SNAPSHOT_DIR) if f.startswith('players_') and f.endswith('.txt')]
    if not files:
        return INIT_PLAYER_FILE
    files_with_path = [os.path.join(SNAPSHOT_DIR, f) for f in files]
    files_with_path.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files_with_path[0]

def read_players_from_txt(path):
    """
    读取玩家数据（支持单行 | 分隔格式，兼容旧多行）
    """
    players = []
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if '|' in content:
        player_strs = content.split('|')
        for ps in player_strs:
            parts = ps.split(',')
            if len(parts) == 3:
                nickname = parts[0]
                level = int(parts[1])
                uid = parts[2]
                players.append((nickname, level, uid))
    else:
        lines = content.splitlines()
        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
            parts = clean_line.split(',')
            if len(parts) == 3:
                nickname = parts[0]
                level = int(parts[1])
                uid = parts[2]
                players.append((nickname, level, uid))
    return players

def fetch_level(player_id):
    url = f"https://chivalry2stats.com/player?id={player_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=(5, 10))
        soup = BeautifulSoup(r.text, 'html.parser')
        texts = list(soup.stripped_strings)
        for i, t in enumerate(texts):
            if t == "Level":
                if i + 1 < len(texts):
                    return int(texts[i + 1])
        for i, t in enumerate(texts):
            if t == "Player Level (XP)":
                if i + 1 < len(texts):
                    return int(texts[i + 1])
        return None
    except (Timeout, ConnectionError) as e:
        print(f"[WARN] 查询 {player_id} 网络超时或连接失败，跳过该玩家。")
        return None
    except Exception as e:
        print(f"[ERROR] 查询 {player_id} 出错，跳过该玩家: {e}")
        return None

def save_snapshot(players_data):
    """
    保存快照为单行 | 分隔格式，无末尾多余换行符
    """
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H%M%S')
    snapshot_path = os.path.join(SNAPSHOT_DIR, f"players_{timestamp}.txt")
    line = '|'.join([f"{nickname},{level},{uid}" for nickname, level, uid in players_data])
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        f.write(line)
    return snapshot_path

def main():
    ensure_dirs()
    yesterday_file = get_latest_snapshot_file()
    print("========================================")
    print("  Chivalry 2 战绩每日检查工具")
    print("========================================")
    print(f"使用基准文件: {yesterday_file}")
    
    old_players = read_players_from_txt(yesterday_file)
    print(f"读取到 {len(old_players)} 位玩家")
    
    success_count = 0
    changed_players = []
    failed_count = 0
    unchanged_count = 0
    max_level_skipped_count = 0
    new_players_data = []

    for nickname, old_level, uid in old_players:
        if old_level >= 1000:
            print(f"玩家 {nickname} 已达 {old_level} 级（≥1000），跳过查询，等级记为 1000。")
            new_level = 1000
            max_level_skipped_count += 1
            unchanged_count += 1
            new_players_data.append((nickname, new_level, uid))
            continue
        
        print(f"查询 {nickname} ({uid}) ...")
        new_level = fetch_level(uid)
        time.sleep(SLEEP_SECONDS)
        if new_level is None:
            failed_count += 1
            new_players_data.append((nickname, old_level, uid))
        else:
            if new_level >= 1000:
                display_level = 1000
                if display_level != old_level:
                    changed_players.append((nickname, old_level, display_level, display_level - old_level))
                else:
                    unchanged_count += 1
                new_players_data.append((nickname, display_level, uid))
            else:
                display_level = new_level
                success_count += 1
                new_players_data.append((nickname, display_level, uid))
                if display_level != old_level:
                    changed_players.append((nickname, old_level, display_level, display_level - old_level))
                else:
                    unchanged_count += 1
    
    now_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    report_path = os.path.join(REPORT_DIR, f"report_{now_str}.txt")
    with open(report_path, 'w', encoding='utf-8') as report_file:
        report_file.write(f"Chivalry 2 等级变化报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. ")
        report_file.write(f"成功查询玩家：{success_count} 位。")
        report_file.write(f" 查询失败：{failed_count} 位。")
        report_file.write(f" 等级未变化：{unchanged_count} 位。")
        report_file.write(f" 已满级(≥1000)跳过检查：{max_level_skipped_count} 位。")
        report_file.write(f" 注：等级≥1000的玩家统一显示为1000。")
        if changed_players:
            report_file.write(f" 等级发生变化：{len(changed_players)} 位：")
            names = [f"{p[0]} {p[1]}→{p[2]}(+{p[3]})" for p in changed_players]
            report_file.write("、".join(names))
        else:
            report_file.write(" 等级发生变化：0 位。")
    
    saved_snapshot = save_snapshot(new_players_data)
    print("========================================")
    print(f"报告已生成: {report_path}")
    print(f"本次快照已保存: {saved_snapshot}")
    print("========================================")
    print("  执行完毕，已自动退出。")

if __name__ == "__main__":
    main()