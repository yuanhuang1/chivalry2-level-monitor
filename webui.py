# webui.py
import sys
import io
# 修复 Windows 控制台中文乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, render_template_string, send_from_directory
import os
import configparser
from datetime import datetime

CONFIG_PATH = 'config.ini'
REPORT_DIR = 'report'
SNAPSHOT_DIR = 'snapshot'

# 读取配置（带容错）
config = configparser.ConfigParser()
webui_port = 5000  # 默认端口
if os.path.exists(CONFIG_PATH):
    config.read(CONFIG_PATH, encoding='utf-8')
    if 'DEFAULT' in config and 'webui_port' in config['DEFAULT']:
        try:
            webui_port = int(config['DEFAULT']['webui_port'])
        except ValueError:
            webui_port = 5000
else:
    # 如果 config.ini 不存在，使用默认端口并提示
    print("[WARN] 未找到 config.ini，使用默认端口 5000")

app = Flask(__name__)

# HTML 模板（内嵌）
INDEX_TPL = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>Chivalry 2 战绩查看器</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        h2 { margin-top: 30px; }
        ul { list-style: none; padding-left: 0; }
        li { margin: 5px 0; }
        a { text-decoration: none; color: #0366d6; }
        a:hover { text-decoration: underline; }
        .btn { display: inline-block; margin: 10px 0; padding: 8px 16px; background: #28a745; color: white; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>Chivalry 2 战绩查看器</h1>
    <a class="btn" href="/run_check">立即检查战绩</a>

    <h2>报告列表</h2>
    <ul>
    {% for r in reports %}
        <li><a href="/report/{{ r }}">{{ r }}</a></li>
    {% else %}
        <li>暂无报告</li>
    {% endfor %}
    </ul>

    <h2>快照列表</h2>
    <ul>
    {% for s in snapshots %}
        <li><a href="/snapshot/{{ s }}">{{ s }}</a></li>
    {% else %}
        <li>暂无快照</li>
    {% endfor %}
    </ul>
</body>
</html>
'''

@app.route('/')
def index():
    reports = sorted(os.listdir(REPORT_DIR)) if os.path.exists(REPORT_DIR) else []
    snapshots = sorted(os.listdir(SNAPSHOT_DIR)) if os.path.exists(SNAPSHOT_DIR) else []
    return render_template_string(INDEX_TPL, reports=reports, snapshots=snapshots)

@app.route('/report/<filename>')
def show_report(filename):
    return send_from_directory(REPORT_DIR, filename, mimetype='text/plain')

@app.route('/snapshot/<filename>')
def show_snapshot(filename):
    return send_from_directory(SNAPSHOT_DIR, filename, mimetype='text/plain')

@app.route('/run_check')
def run_check():
    return '''
    <p>请在服务器上手动运行 <code>python check_script.py</code> 来执行检查。</p>
    <p><a href="/">返回首页</a></p>
    '''

if __name__ == '__main__':
    # 关键改动：host='0.0.0.0' 允许局域网访问
    app.run(host='0.0.0.0', port=webui_port, debug=False)