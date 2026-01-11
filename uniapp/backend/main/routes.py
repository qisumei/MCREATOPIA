import json
import os
from flask import Blueprint, jsonify, request, current_app  # 导入 Flask 的 Blueprint、jsonify、request 和 current_app
from mcstatus import JavaServer  # 导入 mcstatus 库中的 JavaServer 用于查询 Minecraft Java 服状态
import asyncio  # 导入 asyncio 用于异步操作（事件循环、协程等）
import struct  # 导入 struct 用于在 RCON 协议中打包/解包二进制数据
import re  # 导入正则表达式模块用于解析文本
from db import query_db  # 从本地模块 db 导入 query_db 用于执行 SQLite 查询并返回结果

main_bp = Blueprint('main', __name__)  # 创建名为 'main' 的 Blueprint，以便在应用中注册路由

# ==================== RCON 工具 ====================  # 分隔注释：下面是 RCON（远程控制）相关工具函数
SERVERDATA_AUTH = 3  # RCON 协议中表示认证请求的包类型常量
SERVERDATA_EXECCOMMAND = 2  # RCON 协议中表示执行命令的包类型常量

def _build_rcon_packet(request_id: int, packet_type: int, payload: str) -> bytes:  # 构建一个 RCON 协议的数据包（返回字节）
    payload_bytes = payload.encode('utf-8') + b'\x00'  # 将 payload 编码为 UTF-8 字节并在末尾添加一个空字节作为终止符
    size = 4 + 4 + len(payload_bytes) + 1  # 计算包体大小：request_id(4) + type(4) + payload_bytes + 终止符(1)
    return struct.pack(f'<iii{len(payload_bytes)}sb', size, request_id, packet_type, payload_bytes, 0)  # 使用小端格式打包并返回完整二进制包

async def _read_rcon_response(reader: asyncio.StreamReader) -> tuple[int, int, str]:  # 异步读取并解析 RCON 响应包，返回 (request_id, packet_type, payload)
    size_bytes = await reader.readexactly(4)  # 先读取 4 字节包长度字段
    size = struct.unpack('<i', size_bytes)[0]  # 将长度字段按小端 int 解包得到整数大小
    remaining_bytes = await reader.readexactly(size)  # 根据长度读取剩余的包体字节
    request_id, packet_type = struct.unpack('<ii', remaining_bytes[:8])  # 前 8 个字节包含 request_id 和 packet_type
    payload = remaining_bytes[8:-2].decode('utf-8', errors='ignore')  # 剩余部分为 payload（去掉结束的两个字节），使用 utf-8 解码，忽略解码错误
    return request_id, packet_type, payload  # 返回解析结果

async def execute_rcon_command(command: str) -> tuple[bool, str]:  # 异步执行 RCON 命令，返回 (成功标志, 响应文本或错误)
    writer = None  # 初始化 writer 变量以便在 finally 中关闭
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(current_app.config['RCON_IP'], current_app.config['RCON_PORT']), 
            timeout=5.0
        )  # 打开到 RCON 服务的 TCP 连接，最多等待 5 秒
        # 认证
        writer.write(_build_rcon_packet(1, SERVERDATA_AUTH, current_app.config['RCON_PASSWORD']))  # 发送认证包，request_id 设为 1
        await writer.drain()  # 等待写入缓冲区刷新，确保数据已发送
        # 读取认证响应
        for _ in range(2):  # 尝试读取最多两个响应包以确认认证结果
            rid, _, _ = await _read_rcon_response(reader)  # 解析响应包的 request_id（忽略其它字段）
            if rid == 1: break  # 若收到 request_id 为 1 的响应则认证成功，跳出循环
        else:
            return False, "RCON 认证失败"  # 若循环结束仍未认证成功，则返回失败

        # 执行命令
        writer.write(_build_rcon_packet(102, SERVERDATA_EXECCOMMAND, command))  # 发送执行命令包，request_id 设为 102
        await writer.drain()  # 等待写入缓冲区刷新
        
        while True:  # 循环读取响应直到找到与 request_id=102 对应的响应
            rid, _, payload = await _read_rcon_response(reader)  # 读取并解析响应包
            if rid == 102: return True, payload  # 如果 request_id 匹配，则返回成功和响应负载
    except Exception as e:
        return False, str(e)  # 捕获异常并以字符串形式返回错误信息
    finally:
        if writer: writer.close(); await writer.wait_closed()  # 如果 writer 存在则关闭连接并等待关闭完成

def parse_tps_data(text):  # 解析服务器输出的 TPS 文本并返回结构化数据
    text = re.sub(r'§[0-9a-fk-or]', '', text) # 移除文本中的 Minecraft 颜色代码（§ 后跟格式字符）
    pattern = r"Dim\s(-?\d+|Overall)\s\((.*?)\):\sMean\sTPS:\s([\d.]+),\sMean\sTick\sTime:\s([\d.]+)"  # 定义匹配新格式的正则表达式
    matches = re.findall(pattern, text)  # 查找所有匹配项
    if not matches: # 兼容旧格式，如果未匹配到新格式则尝试旧格式的解析
        matches = [(m[0], m[0], m[1], m[2]) for m in re.findall(r'(\w+):\s([\d.]+)\sTPS\s\(([\d.]+)\sms/tick\)', text)]
    
    tps_data = {}  # 初始化返回的字典
    for m in matches:  # 遍历所有匹配结果并规范化维度名称与数值类型
        name = "主世界" if "overworld" in m[1].lower() else ("地狱" if "nether" in m[1].lower() else ("末地" if "end" in m[1].lower() else m[1]))  # 根据关键字翻译维度名称
        tps_data[name] = {"tps": float(m[2]), "mspt": float(m[3])}  # 将 TPS 和 mspt 转换为浮点数并存入字典
    return tps_data  # 返回解析好的数据



# ==================== 路由 ====================  # 路由部分开始

@main_bp.route('/api/server/tps', methods=['GET'])  # 注册 /api/server/tps GET 路由以返回服务器 TPS 信息
def get_tps():
    try:
        loop = asyncio.new_event_loop()  # 创建新的事件循环实例
        asyncio.set_event_loop(loop)  # 将该事件循环设置为当前线程的默认循环
        success, resp = loop.run_until_complete(execute_rcon_command("neoforge tps"))  # 通过 RCON 同步执行 tps 命令并等待结果
        loop.close()  # 关闭事件循环释放资源
        
        if not success: return jsonify({"tps": "20.0", "mspt": "--", "error": "RCON失败"})  # 若 RCON 失败返回默认值与错误信息
        
        data = parse_tps_data(resp)  # 解析返回的 TPS 文本
        main_world = data.get("主世界", data.get("总计", list(data.values())[0] if data else {}))  # 尝试获取主世界或总计或第一个维度的数据
        
        return jsonify({
            "tps": f"{min(main_world.get('tps', 20.0), 20.0):.1f}",  # 返回 tps，最大值限制为 20.0 并格式化为一位小数
            "mspt": f"{main_world.get('mspt', 0.0):.1f}",  # 返回 mspt 并格式化为一位小数
            "dimensions": data  # 返回所有维度的详细数据
        })
    except Exception as e:
        return jsonify({"tps": "20.0", "mspt": "--", "error": str(e)})  # 捕获异常并返回错误信息

@main_bp.route('/api/server/online', methods=['GET'])  # 注册 /api/server/online GET 路由以返回在线玩家信息
def get_online():
    try:
        server = JavaServer.lookup(current_app.config['MC_SERVER_IP'])  # 使用 mcstatus 查找 Minecraft 服务器地址
        status = server.status()  # 获取服务器状态信息（包括玩家、版本、延迟等）
        
        # === 修改开始：构建带头像的玩家列表 ===
        player_list = []  # 初始化玩家列表
        if status.players.sample:  # 如果服务器返回玩家样本（sample）列表
            # 按名字排序，看起来更整齐
            sorted_players = sorted(status.players.sample, key=lambda p: p.name)  # 按玩家名排序样本列表
            for p in sorted_players:  # 遍历排序后的玩家样本
                player_list.append({
                    "name": p.name,  # 玩家名称
                    "id": p.id,  # 玩家 UUID 或 ID
                    # 使用 Crafatar 或类似服务获取玩家头像 URL（此处使用 mc-heads.net）
                    "avatar": f"https://mc-heads.net/head/{p.id}"
                })  # 将包含头像的玩家信息加入列表
        # === 修改结束 ===

        return jsonify({
            "online": status.players.online,  # 当前在线人数
            "max": status.players.max,  # 服务器最大玩家数
            "players": player_list, # 返回增强后的玩家列表（含头像）
            "version": status.version.name,  # 服务器版本名称
            "latency": status.latency  # 与服务器的延迟（毫秒）
        })
    except Exception as e:
        print(f"Error: {e}")  # 打印错误到控制台以便调试
        return jsonify({"online": 0, "max": 0, "players": [], "error": str(e)})  # 出错时返回默认的空信息和错误字符串

@main_bp.route("/api/query-blocks", methods=["GET"])  # 注册 /api/query-blocks GET 路由以查询单个坐标点的方块操作记录
def query_blocks():
    try:
        x, y, z = int(request.args["x"]), int(request.args["y"]), int(request.args["z"])  # 从查询参数中读取 x,y,z 并转换为整数
        world = request.args["world"]  # 获取世界名参数
        
        level = query_db("SELECT id FROM levels WHERE name = ?", (world,), one=True)  # 查询 levels 表获得对应的 level id
        if not level: return jsonify([])  # 若未找到对应世界则返回空列表
        
        sql = "SELECT time,type,user,action FROM blocks WHERE level=? AND x=? AND y=? AND z=? ORDER BY time DESC LIMIT 50"  # 构建 SQL 语句获取最近 50 条记录
        rows = query_db(sql, (level["id"], x, y, z)) or []  # 执行查询，若为空则使用空列表
        
        result = []  # 用于保存返回结果的列表
        for row in rows:  # 遍历每条数据库记录
            mat = query_db("SELECT name FROM materials WHERE id=?", (row["type"],), one=True)  # 根据 type 查找材料名称
            usr = query_db("SELECT name FROM users WHERE id=?", (row["user"],), one=True)  # 根据 user 查找用户名
            result.append({
                "time": row["time"],  # 操作时间
                "action": row["action"],  # 操作类型（放置/破坏等）
                "material": mat["name"] if mat else "未知",  # 材料名或未知
                "username": usr["name"] if usr else "未知"  # 用户名或未知
            })
        return jsonify(result)  # 返回 JSON 格式的结果列表
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 出错时返回 500 状态码并包含错误信息

@main_bp.route("/api/query-range-blocks", methods=["GET"])  # 注册 /api/query-range-blocks GET 路由以进行范围内的方块查询
def query_range_blocks():
    # 范围查询逻辑 (类似上面，略微简化以节省篇幅，核心逻辑已保留)
    try:
        x, y, z = int(request.args["x"]), int(request.args["y"]), int(request.args["z"])  # 读取并转换中心坐标
        r = int(request.args["radius"])  # 读取并转换半径
        world = request.args["world"]  # 读取世界名参数
        
        level = query_db("SELECT id FROM levels WHERE name = ?", (world,), one=True)  # 获取 level id
        if not level: return jsonify([])  # 若未找到世界则返回空列表
        
        sql = "SELECT x,y,z,time,type,user,action FROM blocks WHERE level=? AND x BETWEEN ? AND ? AND y BETWEEN ? AND ? AND z BETWEEN ? AND ? ORDER BY time DESC LIMIT 100"  # 构建范围查询 SQL
        rows = query_db(sql, (level["id"], x-r, x+r, y-r, y+r, z-r, z+r)) or []  # 执行查询并在无结果时使用空列表
        
        result = []  # 初始化结果列表
        for row in rows:  # 遍历查询到的每条记录
            mat = query_db("SELECT name FROM materials WHERE id=?", (row["type"],), one=True)  # 获取材料名称
            usr = query_db("SELECT name FROM users WHERE id=?", (row["user"],), one=True)  # 获取用户名
            result.append({
                "x": row["x"], "y": row["y"], "z": row["z"],  # 坐标
                "time": row["time"], "action": row["action"],  # 时间与操作
                "material": mat["name"] if mat else "未知",  # 材料名或未知
                "username": usr["name"] if usr else "未知"  # 用户名或未知
            })
        return jsonify(result)  # 返回 JSON 结果
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 出错时返回 500 与错误信息