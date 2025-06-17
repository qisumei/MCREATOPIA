from flask import Flask, render_template, jsonify
import subprocess
import threading
import os
import time
import glob
import pyautogui
import pygetwindow as gw
from openai import OpenAI

app = Flask(__name__)

log_buffer = []
max_lines = 200
deepseek_api_key = "sk-a3efed7daec249a295e798e62c3d2eaf"  # 替换为你的密钥
RESTART_TRIGGER_LINES = [
    "Dispatching unloading event for config universalbonemeal-server.toml",
    "Failed to encode packet 'clientbound/minecraft:custom_payload'",
]

def get_latest_log_path():
    log_files = glob.glob("logs/*.log")
    if not log_files:
        return None
    return max(log_files, key=os.path.getmtime)

def start_java_server():
    command = [
        "cmd", "/c", "start", "cmd", "/k",
        'java @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.169/win_args.txt nogui'
    ]
    subprocess.Popen(command, shell=True)
    print("Java服务器已启动")

def send_cmd_to_server(command_text):
    try:
        windows = [w for w in gw.getWindowsWithTitle("java") if w.title.lower().endswith("nogui")]
        if not windows:
            print("找不到 Java CMD 窗口，无法发送指令")
            return
        win = windows[0]
        win.activate()
        time.sleep(0.5)
        pyautogui.typewrite(command_text)
        pyautogui.press('enter')
        print(f"已向服务器发送命令：{command_text}")
    except Exception as e:
        print(f"发送服务器命令失败：{e}")

def monitor_and_restart():
    print("开始监控服务器日志...")

    while True:
        try:
            log_path = get_latest_log_path()
            if not log_path or not os.path.exists(log_path):
                time.sleep(2)
                continue

            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for trigger in RESTART_TRIGGER_LINES:
                if any(trigger in line for line in lines):
                    print(f"检测到触发日志：{trigger}，等待10秒")
                    send_cmd_to_server('tell @a "即将重启服务器剩余10秒"')
                    time.sleep(10)

                    log_path_new = get_latest_log_path()
                    if not log_path_new or not os.path.exists(log_path_new):
                        continue

                    with open(log_path_new, "r", encoding="utf-8", errors="ignore") as f2:
                        last_line = f2.readlines()[-1].strip()

                    if any(trigger in last_line for trigger in RESTART_TRIGGER_LINES):
                        print("服务器似乎卡住了，执行重启")
                        subprocess.call("taskkill /F /IM java.exe", shell=True)
                        time.sleep(3)
                        start_java_server()
                        print("已重启服务器")
                        time.sleep(30)

        except Exception as e:
            print("监控过程中出现错误：", e)

        time.sleep(3)

def tail_forge_log():
    while True:
        log_path = get_latest_log_path()
        if not log_path or not os.path.exists(log_path):
            time.sleep(1)
            continue

        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    log_buffer.append(line.strip())
                    if len(log_buffer) > max_lines:
                        log_buffer.pop(0)
                else:
                    new_path = get_latest_log_path()
                    if new_path != log_path:
                        print(f"日志轮替，重新读取：{new_path}")
                        break
                    time.sleep(0.1)

def extract_errors():
    return [line for line in log_buffer if "java." in line or "Exception" in line]

def explain_errors_via_deepseek(error_log):
    client = OpenAI(
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com"
    )
    messages = [
        {"role": "system", "content": "你是一个擅长 Minecraft 服务器维护的 Java 异常诊断助手，请使用简明 Markdown 格式输出。"},
        {"role": "user", "content": f"以下是日志报错，请帮我分析错误并给出解决建议:\n```\n{error_log}\n```"}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )
    return response.choices[0].message.content

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_log")
def get_log():
    return jsonify({"log": log_buffer[-max_lines:]})

@app.route("/get_errors")
def get_errors():
    return jsonify({"errors": extract_errors()})

@app.route("/analyze_errors")
def analyze_errors():
    errors = "\n".join(extract_errors())
    if not errors.strip():
        return jsonify({"result": "未检测到错误日志。"})
    try:
        result = explain_errors_via_deepseek(errors)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"result": f"调用 DeepSeek API 出错：{e}"})

def launch_forge_server():
    start_java_server()
    threading.Thread(target=monitor_and_restart, daemon=True).start()

if __name__ == "__main__":
    launch_forge_server()
    threading.Thread(target=tail_forge_log, daemon=True).start()
    app.run(debug=True, host="0.0.0.0", port=21003)
