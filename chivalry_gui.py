import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import os
import json
from datetime import datetime
import requests
from requests.exceptions import Timeout, ConnectionError
from bs4 import BeautifulSoup
import sys

# ========== 配置 ==========
INIT_PLAYER_FILE = 'players.txt'
REPORT_DIR = 'report'
SNAPSHOT_DIR = 'snapshot'
CACHE_FILE = 'cache.json'
SLEEP_SECONDS = 10
CACHE_TTL = 12 * 3600
# ==========================

log_text = None  # 全局日志文本框引用

def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发模式和 PyInstaller 打包"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def log(msg):
    def _log():
        if log_text:
            # 修复：把字面上的 \\n 转成真正的换行
            msg_real = msg.replace('\\\n', '\\n')
            log_text.insert(tk.END, msg_real + "\n")
            log_text.see(tk.END)
    log_text.after(0, _log)

def ensure_dirs():
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_cached_level(uid, cache):
    now = int(time.time())
    if uid in cache and now - cache[uid]["timestamp"] < CACHE_TTL:
        return cache[uid]["level"]
    return None

def get_latest_snapshot_file():
    files = [f for f in os.listdir(SNAPSHOT_DIR) if f.startswith('players_') and f.endswith('.txt')]
    if not files:
        return resource_path(INIT_PLAYER_FILE)
    files_with_path = [os.path.join(SNAPSHOT_DIR, f) for f in files]
    files_with_path.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files_with_path[0]

def read_players_from_txt(path):
    players = []
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if '|' in content:
        for ps in content.split('|'):
            parts = ps.split(',')
            if len(parts) == 3:
                players.append((parts[0], int(parts[1]), parts[2]))
    else:
        for line in content.splitlines():
            parts = line.strip().split(',')
            if len(parts) == 3:
                players.append((parts[0], int(parts[1]), parts[2]))
    return players

def fetch_level(player_id):
    url = f"https://chivalry2stats.com/player?id={player_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=(5, 10))
        soup = BeautifulSoup(r.text, 'html.parser')
        texts = list(soup.stripped_strings)
        for i, t in enumerate(texts):
            if t == "Level" and i + 1 < len(texts):
                return int(texts[i + 1])
            if t == "Player Level (XP)" and i + 1 < len(texts):
                return int(texts[i + 1])
        return None
    except Exception as e:
        log(f"[WARN] 查询 {player_id} 出错: {e}")
        return None

def save_snapshot(players_data):
    now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    path = os.path.join(SNAPSHOT_DIR, f"players_{now}.txt")
    line = '|'.join([f"{n},{l},{u}" for n, l, u in players_data])
    with open(path, 'w', encoding='utf-8') as f:
        f.write(line)
    return path

def run_check():
    def task():
        log("========================================")
        log("  Chivalry 2 战绩每日检查工具（GUI版）")
        log("========================================")
        ensure_dirs()
        snap = get_latest_snapshot_file()
        log(f"使用基准文件: {snap}")
        players = read_players_from_txt(snap)
        log(f"读取到 {len(players)} 位玩家")

        cache = load_cache()
        success_count = changed_count = failed_count = unchanged_count = max_skip = cached_count = 0
        new_data = []
        changed_players = []  # 用于记录变化详情

        for nick, old_lvl, uid in players:
            if old_lvl >= 1000:
                log(f"{nick} 已满级({old_lvl})，跳过。")
                new_data.append((nick, 1000, uid))
                max_skip += 1
                unchanged_count += 1
                continue

            cached = get_cached_level(uid, cache)
            if cached is not None:
                log(f"{nick} 使用缓存等级 {cached}，跳过网络查询。")
                new_data.append((nick, cached, uid))
                success_count += 1
                cached_count += 1
                if cached != old_lvl:
                    changed_players.append((nick, old_lvl, cached, cached - old_lvl))
                    changed_count += 1
                else:
                    unchanged_count += 1
                continue

            log(f"查询 {nick} ({uid}) ...")
            lvl = fetch_level(uid)
            time.sleep(SLEEP_SECONDS)
            if lvl is None:
                log(f"{nick} 查询失败，保留旧等级。")
                new_data.append((nick, old_lvl, uid))
                failed_count += 1
            else:
                display = 1000 if lvl >= 1000 else lvl
                if display < 1000:
                    cache[uid] = {"level": display, "timestamp": int(time.time())}
                new_data.append((nick, display, uid))
                success_count += 1
                if display != old_lvl:
                    changed_players.append((nick, old_lvl, display, display - old_lvl))
                    changed_count += 1
                else:
                    unchanged_count += 1

        save_cache(cache)

        now_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        report_path = os.path.join(REPORT_DIR, f"report_{now_str}.txt")
        with open(report_path, 'w', encoding='utf-8') as rf:
            rf.write(f"Chivalry 2 等级变化报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            rf.write(f"成功查询玩家：{success_count} 位。\n")
            rf.write(f"其中通过缓存查询：{cached_count} 位。\n")
            rf.write(f"查询失败：{failed_count} 位。\n")
            rf.write(f"等级未变化：{unchanged_count} 位。\n")
            rf.write(f"已满级(≥1000)跳过检查：{max_skip} 位。\n")
            rf.write(f"注：等级≥1000的玩家统一显示为1000。\n")
            if changed_players:
                rf.write(f"等级发生变化：{len(changed_players)} 位：\n")
                for p in changed_players:
                    rf.write(f"{p[0]} {p[1]}→{p[2]}(+{p[3]})\n")
            else:
                rf.write("等级发生变化：0 位。\n")
        log(f"报告已生成: {report_path}")
        snap_path = save_snapshot(new_data)
        log(f"快照已保存: {snap_path}")

        # 在日志中也输出缓存数量
        log(f"本次通过缓存查询的玩家：{cached_count} 位")
        log("========================================")
        log("执行完毕。")
    threading.Thread(target=task, daemon=True).start()


def run_clear_cache():
    def task():
        if not os.path.exists(CACHE_FILE):
            log("[INFO] 无缓存文件。")
            return
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            try:
                cache = json.load(f)
            except:
                cache = {}
        count = len(cache)
        ans = messagebox.askyesno("清理缓存", f"当前缓存 {count} 条，是否删除？")
        if ans:
            os.remove(CACHE_FILE)
            log("[DONE] 缓存文件已删除。")
        else:
            log("[CANCEL] 已取消删除。")
    threading.Thread(target=task, daemon=True).start()

def main():
    global log_text
    root = tk.Tk()
    root.title("Chivalry 2 等级检查工具")
    root.geometry("700x500")

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="开始检查", width=12, command=run_check).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="清理缓存", width=12, command=run_clear_cache).pack(side=tk.LEFT, padx=5)

    log_text = scrolledtext.ScrolledText(root, state='normal', wrap='word')
    log_text.pack(fill='both', expand=True, padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()