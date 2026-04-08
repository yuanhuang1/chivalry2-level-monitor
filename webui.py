# webui.py
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, render_template_string, send_from_directory
import os
import configparser
from datetime import datetime
import subprocess
import threading  # 新增：用于后台线程

CONFIG_PATH = 'config.ini'
REPORT_DIR = 'report'
SNAPSHOT_DIR = 'snapshot'

# ===== 配置读取（无错误字符）=====
webui_port = 5000  # 默认端口
if os.path.exists(CONFIG_PATH):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')
    if config.has_section('DEFAULT') and config.has_option('DEFAULT', 'webui_port'):
        try:
            webui_port = int(config.get('DEFAULT', 'webui_port'))
        except ValueError:
            webui_port = 5000
# ==================================

app = Flask(__name__)

def get_file_info(file_list, dir_path):
    info = []
    for fname in file_list:
        fpath = os.path.join(dir_path, fname)
        mtime = os.path.getmtime(fpath)
        mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        info.append((fname, mtime_str))
    info.sort(key=lambda x: x[1], reverse=True)
    return info

INDEX_TPL = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>Chivalry 2 等级监控查看器</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        h2 { margin-top: 30px; }
        ul { list-style: none; padding-left: 0; }
        li { margin: 8px 0; padding: 6px; border-bottom: 1px solid #eee; }
        a { text-decoration: none; color: #0366d6; font-weight: bold; }
        a:hover { text-decoration: underline; }
        .btn { display: inline-block; margin: 10px 0; padding: 8px 16px; background: #28a745; color: white; border-radius: 4px; }
        .time { color: #666; font-size: 0.9em; margin-left: 10px; }
        .new { background-color: #e7f4e4; }
    </style>
</head>
<body>
    <h1>Chivalry 2 等级监控查看器</h1>
    <a class="btn" href="/run_check">立即检查等级</a>
    <h2>报告列表</h2>
    <ul>
    {% for r, t in reports %}
        <li class="{{ 'new' if loop.first }}">&#128196; <a href="/report/{{ r }}">{{ r }}</a><span class="time">生成时间：{{ t }}</span></li>
    {% else %}
        <li>暂无报告</li>
    {% endfor %}
    </ul>
    <h2>快照列表</h2>
    <ul>
    {% for s, t in snapshots %}
        <li class="{{ 'new' if loop.first }}">&#128202; <a href="/snapshot/{{ s }}">{{ s }}</a><span class="time">生成时间：{{ t }}</span></li>
    {% else %}
        <li>暂无快照</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/')
def index():
    reports_raw = sorted(os.listdir(REPORT_DIR)) if os.path.exists(REPORT_DIR) else []
    snapshots_raw = sorted(os.listdir(SNAPSHOT_DIR)) if os.path.exists(SNAPSHOT_DIR) else []
    reports = get_file_info(reports_raw, REPORT_DIR)
    snapshots = get_file_info(snapshots_raw, SNAPSHOT_DIR)
    return render_template_string(INDEX_TPL, reports=reports, snapshots=snapshots)

@app.route('/report/<filename>')
def show_report(filename):
    return send_from_directory(REPORT_DIR, filename, mimetype='text/plain')

@app.route('/snapshot/<filename>')
def show_snapshot(filename):
    return send_from_directory(SNAPSHOT_DIR, filename, mimetype='text/plain')

@app.route('/run_check')
def run_check():
    def run_script():
        try:
            # 同步执行脚本，但放在后台线程里
            result = subprocess.run(
                ['python', 'check_script.py'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=600  # 最长等 10 分钟
            )
            stdout = result.stdout if result.stdout is not None else ""
            stderr = result.stderr if result.stderr is not None else ""
            output = stdout + stderr
            # 将日志保存到文件，方便排查
            with open("last_run.log", "w", encoding="utf-8") as f:
                f.write(output)
        except subprocess.TimeoutExpired:
            with open("last_run.log", "w", encoding="utf-8") as f:
                f.write("等级检查超时（超过 10 分钟）")
        except Exception as e:
            with open("last_run.log", "w", encoding="utf-8") as f:
                f.write(str(e))

    # 启动后台线程执行脚本
    thread = threading.Thread(target=run_script)
    thread.daemon = True  # 主程序退出时线程也会结束
    thread.start()

    return '''
    <p>等级检查已在后台启动，请稍后到“报告列表”查看最新结果。</p>
    <p><a href="/">返回首页</a></p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=webui_port, debug=False)