from flask import Flask, render_template, jsonify, request,send_from_directory
import subprocess
import threading
import os
import time
# import psutil
# import signal
import logging
from logging.handlers import TimedRotatingFileHandler
from concurrent.futures import ThreadPoolExecutor
import shutil
import atexit

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
    "log_file": "server_activity.log",
    "server_port": 21009
}

# 初始化全局变量
log_buffer = []
server_process = None  # 直接跟踪进程对象
log_lock = threading.Lock()  # 线程锁
executor = ThreadPoolExecutor(max_workers=4)  # 异步任务
start_lock = threading.Lock()  # 启动锁防止并发启动

# 日志配置
log_handler = TimedRotatingFileHandler(CONFIG['log_file'], when="midnight", interval=1)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

def is_server_running():
    """检查服务器是否在运行"""
    if server_process and server_process.poll() is None:
        return True
    
    # 备用检查：通过端口检测
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex(('127.0.0.1', 25565))
        return result == 0
    except:
        return False

def start_java_server():
    """启动Java服务器进程"""
    global server_process
    
    # 避免重复启动
    with start_lock:
        if is_server_running():
            app.logger.warning("服务器已在运行中，无需重复启动")
            return False

        try:
            # 查找Java路径
            java_path = shutil.which("java") or "java.exe"
            
            # 创建必要的文件
            for file_path, default_content in [
                ("user_jvm_args.txt", "-Xmx2G\n-Dfile.encoding=UTF-8"),
                ("eula.txt", "eula=true")
            ]:
                if not os.path.exists(file_path):
                    with open(file_path, "w") as f:
                        f.write(default_content)
                    app.logger.info(f"创建默认文件: {file_path}")
            # 检测neoforge版本
            forge_root = os.path.join("libraries", "net", "neoforged", "neoforge")
            if not os.path.exists(forge_root):
                app.logger.error(f"Forge安装目录不存在: {forge_root}")
                return False
            # 获取所有可用的neoforge版本
            forge_versions = []
            for entry in os.listdir(forge_root):
                entry_path = os.path.join(forge_root, entry)
                if os.path.isdir(entry_path):
                    win_args_path = os.path.join(entry_path, "win_args.txt")
                    if os.path.exists(win_args_path):
                        forge_versions.append(entry)
            
            if not forge_versions:
                app.logger.error("致命错误：未找到任何有效的neoforge安装版本")
                return False
            def parse_version(version_str):
                """将版本字符串解析为可比较的元组"""
                # 移除非数字字符，只保留数字和点
                clean_version = ''.join(c for c in version_str if c.isdigit() or c == '.')
                return tuple(map(int, clean_version.split('.')))
            # 按版本号排序（从高到低）
            forge_versions.sort(key=parse_version, reverse=True)
            selected_version = forge_versions[0]
            win_args_path = os.path.join(forge_root, selected_version, "win_args.txt")
            app.logger.info(f"检测到neoforge版本: {selected_version}")
            # 启动命令
            command = [
                java_path,
                "-Xms512M",
                "-Xmx4G",
                f"@{win_args_path}",
                "nogui"
            ]
            
            app.logger.info(f"启动服务器命令: {' '.join(command)}")
            
            # 启动进程
            server_process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 启动日志收集线程
            threading.Thread(target=capture_server_logs, daemon=True).start()
            app.logger.info("服务器启动成功")
            return True
            
        except Exception as e:
            app.logger.exception(f"启动异常: {str(e)}")
            return False

def capture_server_logs():
    """捕获服务器日志输出"""
    global log_buffer
    
    while server_process.poll() is None:  # 进程仍在运行
        try:
            line = server_process.stdout.readline()
            if line:
                line = line.strip()
                with log_lock:
                    log_buffer.append(line)
                    if len(log_buffer) > CONFIG['max_log_lines']:
                        log_buffer.pop(0)
                
                # 实时记录到日志文件
                app.logger.info(f"SERVER: {line}")
        except Exception as e:
            app.logger.error(f"日志捕获异常: {e}")
            break
    
    app.logger.info("日志捕获线程已退出")

def terminate_server():
    """终止服务器进程"""
    global server_process
    
    if not server_process:
        return
    
    try:
        # 尝试关闭
        server_process.stdin.write("stop\n")
        server_process.stdin.flush()
        app.logger.info("已发送停止命令")
        
        # 等待最多10秒
        for _ in range(10):
            if server_process.poll() is not None:
                break
            time.sleep(1)
        
        # 强制终止如果仍然运行
        if server_process.poll() is None:
            server_process.terminate()
            app.logger.warning("强制终止服务器进程")
        
        server_process = None
    
    except Exception as e:
        app.logger.error(f"终止服务器错误: {e}")
        try:
            # 最终尝试终止
            if server_process.poll() is None:
                server_process.kill()
        except:
            pass
        finally:
            server_process = None

def send_cmd_to_server(command_text):
    """向服务器发送命令"""
    if not server_process or server_process.poll() is not None:
        return False
    
    try:
        # 添加换行符以确保命令执行
        command_text = command_text.strip() + "\n"
        server_process.stdin.write(command_text)
        server_process.stdin.flush()
        app.logger.info(f"命令已发送: {command_text.strip()}")
        return True
    except Exception as e:
        app.logger.error(f"发送命令失败: {e}")
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
                    if start_java_server():
                        app.logger.info("服务器重启成功")
                        last_restart_time = current_time
                else:
                    app.logger.info(f"重启冷却中: {int(cooldown_remaining)}秒")
                time.sleep(10)
                continue

            # 日志触发检测
            with log_lock:
                recent_logs = log_buffer[-50:] if log_buffer else []
                
            for trigger in CONFIG['restart_triggers']:
                if any(trigger in line for line in recent_logs):
                    app.logger.warning(f"检测到触发条件: {trigger}")
                    send_cmd_to_server('tell @a "服务器将在10秒后重启"')
                    time.sleep(10)
                    
                    if is_server_running():
                        # 发送正常停止命令
                        send_cmd_to_server("stop")
                        time.sleep(5)
                    
                    if not is_server_running() and start_java_server():
                        last_restart_time = time.time()
                        app.logger.info("已完成重启")
                    else:
                        app.logger.info("服务器恢复运行，取消重启")
                    break  # 一次只处理一个触发条件

        except Exception as e:
            app.logger.error(f"监控异常: {e}")
            time.sleep(5)
        
        time.sleep(CONFIG['server_check_interval'])

@app.route("/")
def index():
    return render_template("index.html")
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)
@app.route("/start-server", methods=["POST"])
def start_server():
    """启动服务器API"""
    success = start_java_server()
    return jsonify({"success": success})

@app.route("/stop-server", methods=["POST"])
def stop_server():
    """停止服务器API"""
    terminate_server()
    return jsonify({"success": True})

@app.route("/restart-server", methods=["POST"])
def restart_server():
    """重启服务器API"""
    terminate_server()
    time.sleep(2)
    success = start_java_server()
    return jsonify({"success": success})

@app.route("/get_log")
def get_log():
    """分页获取日志"""
    page = request.args.get("page", 1, type=int)
    per_page = 100
    with log_lock:
        if not log_buffer:
            return jsonify({"log": [], "total_pages": 1, "current_page": 1})
            
        total = len(log_buffer)
        pages = (total - 1) // per_page + 1
        start_idx = max(0, min(total, (page-1)*per_page))
        end_idx = min(total, page*per_page)
        log_data = log_buffer[start_idx:end_idx]
        
    return jsonify({
        "log": log_data,
        "total_pages": pages,
        "current_page": page
    })

@app.route("/get_errors")
def get_errors():
    with log_lock:
        if not log_buffer:
            return jsonify({"errors": []})
            
        errors = [
            line for line in log_buffer[-100:]  # 只检查最近100行
            if any(keyword in line for keyword in ["ERROR", "Exception", "java.", "Crash"])
        ][-10:]  # 仅返回最新10条
        
    return jsonify({"errors": errors})

@app.route("/analyze_errors")
def analyze_errors():
    """异步错误分析"""
    from . import extract_errors  # 从上面的函数获取错误
    with log_lock:
        errors = "\n".join(extract_errors())
    
    future = executor.submit(explain_errors_via_deepseek, errors)
    return jsonify({"status": "processing", "task_id": "task_" + str(future)})

@app.route("/task_result/<task_id>")
def task_result(task_id):
    """获取异步任务结果"""
    # 简化处理，实际应用中应跟踪任务状态
    from . import extract_errors
    with log_lock:
        errors = "\n".join(extract_errors())
    result = explain_errors_via_deepseek(errors)
    return jsonify({"result": result})

@app.route("/health")
def health_check():
    """心跳检查接口"""
    pid = server_process.pid if server_process and server_process.poll() is None else None
    return jsonify({
        "status": "running" if is_server_running() else "down",
        "log_entries": len(log_buffer) if log_buffer else 0,
        "server_pid": pid
    })

@app.route("/send-command", methods=["POST"])
def send_command():
    """服务器发送命令API"""
    data = request.get_json()
    command = data.get("command", "")
    if not command:
        return jsonify({"success": False, "error": "Empty command"})
    
    success = send_cmd_to_server(command)
    return jsonify({"success": success})

def explain_errors_via_deepseek(error_log):
    """AI错误分析"""
    if not error_log or not error_log.strip():
        return "未检测到有效错误日志"
    
    # 在实际应用中，这里会调用DeepSeek API
    # 以下是模拟响应
    return f"""
**AI错误分析结果** (模拟)

### 检测到的问题
- Mod冲突：`universalbonemeal-mod` 和 `neoforge-core` 的API不兼容
- 配置文件错误：`universalbonemeal-server.toml` 配置损坏

### 解决方案
1. 删除 `config/universalbonemeal-server.toml` 文件
2. 重新下载并安装 UniversalBonemeal 4.2.1+ 版本
3. 重启服务器应用配置更改

如果问题仍然存在，请尝试逐步禁用可疑Mod来排查问题。
"""
    
def init_server():
    """初始化服务器"""
    app.logger.info("===== 服务器初始化开始 =====")
    app.logger.info(f"工作目录: {os.getcwd()}")
    
    # 确保服务器进程在退出时被终止
    atexit.register(terminate_server)
    
    # 创建必要的目录结构
    os.makedirs("logs", exist_ok=True)
    
    if not is_server_running():
        app.logger.info("尝试启动服务器...")
        start_java_server()
    else:
        app.logger.info("服务器已经在运行")
    
    # 启动监控线程
    threading.Thread(target=monitor_and_restart, daemon=True).start()
    app.logger.info("服务器监控线程已启动")

if __name__ == "__main__":
    # 依赖检查
    required_libs = ['psutil']
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            app.logger.warning(f"缺少依赖库: {lib}，尝试安装...")
            subprocess.call(["pip", "install", lib])
    
    # 生产模式运行 
    init_server()
    app.run(
        host="0.0.0.0", 
        port=CONFIG['server_port'], 
        debug=False, 
        use_reloader=False
    )