from flask import Flask, render_template, jsonify, request
import subprocess
import threading
import os
import time
import glob
import pyautogui
import pygetwindow as gw
from openai import OpenAI
import psutil
import signal
import logging
from logging.handlers import TimedRotatingFileHandler
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# 配置管理
CONFIG = {
    "max_log_lines": 500,
    "restart_triggers": [
        "Dispatching unloading event for config universalbonemeal-server.toml",
        "Failed to encode packet 'clientbound/minecraft:custom_payload'"
    ],
    "server_check_interval": 1,
    "restart_cooldown": 60,
    "log_file": "server_activity.log"
}

# 初始化全局变量
log_buffer = []
server_pid = None  # PID
log_lock = threading.Lock()  # 线程锁
executor = ThreadPoolExecutor(max_workers=4)  # 异步任务

# 日志配置
log_handler = TimedRotatingFileHandler(CONFIG['log_file'], when="midnight", interval=1)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)
# DeepseekApi key 
deepseek_api_key = ""

def is_server_running():
    """检测服务器进程PID"""
    global server_pid
    if server_pid and psutil.pid_exists(server_pid):
        return True
    return False

def start_java_server():
    """启动服务器并记录PID"""
    global server_pid
    command = [
        "cmd", "/c", "start", "cmd", "/k",
        'java @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.179/win_args.txt %* nogui'
    ]
    proc = subprocess.Popen(command, shell=True)
    server_pid = proc.pid
    app.logger.info(f"Java服务器已启动 PID: {server_pid}")

def terminate_server():
    """终止服务器进程 根据PID"""
    global server_pid
    if server_pid:
        try:
            os.kill(server_pid, signal.SIGTERM)
            app.logger.info(f"已终止服务器进程 PID: {server_pid}")
        except ProcessLookupError:
            app.logger.warning("服务器进程已终止")
    server_pid = None

def get_latest_log_path():
    """根据时间获取最新日志文件路径"""
    try:
        log_files = glob.glob("logs/*.log")
        return max(log_files, key=os.path.getmtime) if log_files else None
    except Exception as e:
        app.logger.error(f"获取日志路径失败: {e}")
        return None

def send_cmd_to_server(command_text):
    """向服务器发送命令"""
    try:
        windows = [w for w in gw.getWindowsWithTitle("cmd") if "nogui" in w.title.lower()]
        if not windows:
            app.logger.warning("找不到CMD窗口")
            return False
            
        win = windows[0]
        win.activate()
        time.sleep(0.5)
        pyautogui.typewrite(command_text)
        pyautogui.press('enter')
        app.logger.info(f"命令已发送: {command_text}")
        return True
    except Exception as e:
        app.logger.error(f"命令发送失败: {e}")
        return False

def monitor_and_restart():
    """服务器监控与自动重启"""
    app.logger.info("启动服务器监控线程")
    last_restart_time = 0

    while True:
        try:
            # 检测服务器状态
            if not is_server_running():
                current_time = time.time()
                cooldown_remaining = CONFIG['restart_cooldown'] - (current_time - last_restart_time)
                
                if cooldown_remaining <= 0:
                    app.logger.warning("检测到服务器关闭，执行重启...")
                    terminate_server()
                    time.sleep(3)
                    start_java_server()
                    last_restart_time = current_time
                    time.sleep(30)  # 等待启动完成
                else:
                    app.logger.info(f"重启冷却中: {int(cooldown_remaining)}秒")
                time.sleep(5)
                continue

            # 日志触发检测
            log_path = get_latest_log_path()
            if not log_path:
                time.sleep(2)
                continue

            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for trigger in CONFIG['restart_triggers']:
                if any(trigger in line for line in lines[-50:]):  # 仅检查最新日志
                    app.logger.warning(f"检测到触发条件: {trigger}")
                    send_cmd_to_server('tell @a "服务器将在10秒后重启"')
                    time.sleep(10)
                    
                    # 二次确认是否卡死
                    if is_server_running():
                        app.logger.info("服务器恢复运行，取消重启")
                    else:
                        terminate_server()
                        time.sleep(3)
                        start_java_server()
                        last_restart_time = time.time()
                        app.logger.info("已完成重启")

        except Exception as e:
            app.logger.error(f"监控异常: {e}")
        
        time.sleep(CONFIG['server_check_interval'])

def tail_forge_log():
    """日志追踪线程"""
    app.logger.info("启动日志监控线程")
    current_path = None
    
    while True:
        new_path = get_latest_log_path()
        if not new_path:
            time.sleep(1)
            continue
            
        if new_path != current_path:
            app.logger.info(f"检测到新日志文件: {new_path}")
            current_path = new_path
        
        try:
            with open(current_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if line:
                        with log_lock:  # 线程锁
                            log_buffer.append(line.strip())
                            if len(log_buffer) > CONFIG['max_log_lines']:
                                log_buffer.pop(0)
                    else:
                        time.sleep(0.5)
        except Exception as e:
            app.logger.error(f"日志读取失败: {e}")
            time.sleep(1)

def extract_errors():
    """提取错误日志"""
    with log_lock:
        return [
            line for line in log_buffer 
            if any(keyword in line for keyword in ["ERROR", "Exception", "java.", "Crash"])
        ][-10:]  # 仅返回最新10条

def explain_errors_via_deepseek(error_log):
    """异步调用DeepSeek API"""
    if not deepseek_api_key:
        return "未配置DeepSeek API密钥"
    
    if not error_log.strip():
        return "未检测到有效错误日志"
    
    try:
        client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是有10年经验的Minecraft服务器专家，用Markdown格式回答"},
                {"role": "user", "content": f"分析以下错误并给出解决方案:\n```\n{error_log}\n```"}
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API调用失败: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_log")
def get_log():
    """分页获取日志"""
    page = request.args.get("page", 1, type=int)
    start_idx = (page-1) * 100
    end_idx = page * 100
    with log_lock:
        return jsonify({"log": log_buffer[start_idx:end_idx], "total_pages": len(log_buffer)//100+1})

@app.route("/get_errors")
def get_errors():
    with log_lock:
        return jsonify({"errors": extract_errors()})

@app.route("/analyze_errors")
def analyze_errors():
    """异步错误分析"""
    errors = "\n".join(extract_errors())
    future = executor.submit(explain_errors_via_deepseek, errors)
    return jsonify({"status": "processing", "task_id": str(future)})

@app.route("/task_result/<task_id>")
def task_result(task_id):
    """获取异步任务结果"""
    for future in [f for f in executor._futures if str(f) == task_id]:
        if future.done():
            return jsonify({"result": future.result()})
    return jsonify({"status": "pending"})

@app.route("/health")
def health_check():
    """心跳检查接口"""
    return jsonify({
        "status": "running" if is_server_running() else "down",
        "uptime": time.time() - start_time,
        "log_entries": len(log_buffer)
    })


def init_server():
    """初始化服务器"""
    global start_time
    start_time = time.time()
    
    if not is_server_running():
        start_java_server()
    
    threading.Thread(target=monitor_and_restart, daemon=True).start()
    threading.Thread(target=tail_forge_log, daemon=True).start()

if __name__ == "__main__":
    # 依赖检查
    required_libs = ['psutil', 'pyautogui', 'pygetwindow','logging']
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            subprocess.call(["pip", "install", lib])
    
    # 生产模式运行 
    init_server()
    app.run(host="0.0.0.0", port=21009, debug=False)