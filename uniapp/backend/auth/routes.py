from flask import Blueprint, jsonify, request, redirect, current_app  # 导入 Flask 核心组件
import requests  # 导入 requests 库用于发送 HTTP 请求
import minecraft_launcher_lib  # 导入第三方库用于获取微软登录链接
import json # 导入 json 库用于解析白名单文件
import os # 导入 os 库用于处理文件路径

auth_bp = Blueprint('auth', __name__)  # 创建名为 'auth' 的蓝图

# 辅助函数：手动获取 Minecraft Profile
def manual_get_minecraft_profile(auth_code):
    print("[1/4] 正在获取微软 Access Token...")  # 打印日志：开始第一步
    token_url = "https://login.live.com/oauth20_token.srf"  # 定义微软 Token 接口地址
    data = {
        "client_id": current_app.config['CLIENT_ID'],  # 获取配置中的 Client ID
        "client_secret": current_app.config['CLIENT_SECRET'],  # 获取配置中的 Client Secret
        "code": auth_code,  # 传入授权码
        "grant_type": "authorization_code",  # 指定授权类型
        "redirect_uri": current_app.config['REDIRECT_URI']  # 获取配置中的回调地址
    }
    resp = requests.post(token_url, data=data)  # 发送 POST 请求获取 Token
    if resp.status_code != 200:
        raise Exception(f"微软授权失败 (HTTP {resp.status_code}): {resp.text}")  # 失败则抛出异常
    
    ms_token = resp.json()["access_token"]  # 提取 Access Token
    
    print("[2/4] 正在获取 Xbox Live Token...")  # 打印日志：开始第二步
    xbox_auth_url = "https://user.auth.xboxlive.com/user/authenticate"  # 定义 Xbox 验证接口
    xbox_payload = {
        "Properties": {
            "AuthMethod": "RPS",  # 验证方法
            "SiteName": "user.auth.xboxlive.com",  # 站点名称
            "RpsTicket": f"d={ms_token}"  # 传入微软 Token
        },
        "RelyingParty": "http://auth.xboxlive.com",  # 依赖方地址
        "TokenType": "JWT"  # Token 类型
    }
    resp = requests.post(xbox_auth_url, json=xbox_payload)  # 发送 POST 请求获取 Xbox Token
    if resp.status_code != 200:
        raise Exception(f"Xbox 验证失败: {resp.text}")  # 失败则抛出异常
    
    xbox_data = resp.json()  # 解析响应 JSON
    xbox_token = xbox_data["Token"]  # 提取 Xbox Token
    user_hash = xbox_data["DisplayClaims"]["xui"][0]["uhs"]  # 提取用户 Hash (UHS)
    
    print("[3/4] 正在获取 XSTS Token...")  # 打印日志：开始第三步
    xsts_url = "https://xsts.auth.xboxlive.com/xsts/authorize"  # 定义 XSTS 验证接口
    xsts_payload = {
        "Properties": {
            "SandboxId": "RETAIL",  # 沙盒 ID
            "UserTokens": [xbox_token]  # 传入 Xbox Token
        },
        "RelyingParty": "rp://api.minecraftservices.com/",  # 依赖方为 Minecraft 服务
        "TokenType": "JWT"
    }
    resp = requests.post(xsts_url, json=xsts_payload)  # 发送 POST 请求获取 XSTS Token
    if resp.status_code != 200:
        raise Exception(f"XSTS 验证失败: {resp.text}")  # 失败则抛出异常
        
    xsts_token = resp.json()["Token"]  # 提取 XSTS Token
    
    print("[4/4] 正在获取 Minecraft 档案...")  # 打印日志：开始第四步
    mc_auth_url = "https://api.minecraftservices.com/authentication/login_with_xbox"  # Minecraft 登录接口
    mc_payload = {
        "identityToken": f"XBL3.0 x={user_hash};{xsts_token}"  # 构造认证 Token
    }
    resp = requests.post(mc_auth_url, json=mc_payload)  # 发送 POST 请求进行登录
    if resp.status_code != 200:
        raise Exception(f"Minecraft 登录失败: {resp.text}")  # 失败则抛出异常
        
    mc_access_token = resp.json()["access_token"]  # 提取 Minecraft Access Token
    
    profile_url = "https://api.minecraftservices.com/minecraft/profile"  # 档案获取接口
    headers = {"Authorization": f"Bearer {mc_access_token}"}  # 设置请求头
    resp = requests.get(profile_url, headers=headers)  # 发送 GET 请求获取档案
    
    if resp.status_code != 200:
        raise Exception(f"无法获取档案: {resp.text}")  # 失败则抛出异常
        
    return resp.json()  # 返回玩家档案 JSON

def check_whitelist_logic(user_uuid):  # 检查传入的 UUID 是否在 whitelist.json 中
    whitelist_path = os.path.join(current_app.root_path, 'whitelist.json')  # 计算 whitelist.json 的绝对路径

    if not os.path.exists(whitelist_path):  # 如果白名单文件不存在
        return False  # 则认为用户不在白名单中

    try:
        # 预处理 API 传来的 UUID：去掉横杠，转小写以便比较
        clean_api_uuid = user_uuid.replace('-', '').lower()  # 清洗 API 提供的 uuid

        with open(whitelist_path, 'r', encoding='utf-8') as f:  # 打开白名单文件（只读）
            data = json.load(f)  # 将 JSON 内容解析为 Python 对象（一般为列表）
            for user in data:  # 遍历每个白名单条目
                json_uuid = user.get('uuid', '')  # 从条目中安全获取 uuid 字段
                clean_json_uuid = json_uuid.replace('-', '').lower()  # 清洗 JSON 中的 uuid

                if clean_json_uuid == clean_api_uuid:  # 如果两端 uuid 匹配
                    return True  # 则用户在白名单中，返回 True
        return False  # 完整遍历后未匹配则返回 False
    except Exception as e:  # 读取或解析过程出错
        print(f"白名单读取错误: {e}")  # 打印异常信息以便调试
        return False  # 出错时安全地返回 False
    

def check_op_status(user_uuid):
    """
    检查用户是否在 ops.json 中，并返回 level
    返回: int (0 表示不是 OP, 1-4 表示 OP 等级)
    """
    # 假设 ops.json 也在根目录
    ops_path = os.path.join(current_app.root_path, 'ops.json')
    
    if not os.path.exists(ops_path):
        return 0
    
    try:
        # 预处理 API 传来的 UUID：去掉横杠，转小写
        clean_api_uuid = user_uuid.replace('-', '').lower()
        
        with open(ops_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 标准 MC ops.json 是一个列表
            for user in data:
                json_uuid = user.get('uuid', '')
                clean_json_uuid = json_uuid.replace('-', '').lower()
                
                if clean_json_uuid == clean_api_uuid:
                    # 获取权限等级，默认为 4 (最高)
                    return user.get('level', 4)
                    
        return 0 # 未找到
    except Exception as e:
        print(f"OP名单读取错误: {e}")
        return 0

@auth_bp.route('/api/auth/microsoft')  # 登录跳转路由：将用户重定向到微软登录页面
def login_microsoft():  # 生成并重定向到微软 OAuth 登录 URL
    try:
        login_url = minecraft_launcher_lib.microsoft_account.get_login_url(
            client_id=current_app.config['CLIENT_ID'],  # 从配置获取 Client ID
            redirect_uri=current_app.config['REDIRECT_URI']  # 从配置获取回调地址
        )
        return redirect(login_url)  # 重定向至微软登录页
    except Exception as e:
        return f"生成链接失败: {str(e)}"  # 返回错误信息
    

@auth_bp.route('/api/whitelist/check', methods=['GET'])  # 提供一个检查白名单的简单 API
def check_whitelist():  # 处理 /api/whitelist/check 请求
    uuid = request.args.get('uuid')  # 从查询参数中获取 uuid

    if not uuid:  # 如果没有提供 uuid 参数
        return jsonify({'error': '缺少 UUID 参数', 'whitelisted': False}), 400  # 返回 400 Bad Request

    is_whitelisted = check_whitelist_logic(uuid)  # 调用白名单检查逻辑获得结果
    op_level = check_op_status(uuid)

    return jsonify({  # 返回 JSON 格式的检查结果
        'uuid': uuid,  # 原始 uuid
        'whitelisted': is_whitelisted,  # 是否在白名单中
        'op_level': op_level  # 新增返回字段
    })

@auth_bp.route('/callback')  # 登录回调路由
def auth_callback():
    auth_code = request.args.get('code')  # 获取回调参数中的 code
    if not auth_code:
        return "No code received."  # 若无 code 则中止
    
    try:
        profile = manual_get_minecraft_profile(auth_code)  # 获取玩家档案
        mc_name = profile["name"]  # 提取玩家名称
        mc_uuid = profile["id"]  # 提取玩家 UUID
        
        # 新增步骤：检查是否在白名单中
        is_whitelisted = check_whitelist_logic(mc_uuid)
        whitelist_str = "true" if is_whitelisted else "false"  # 转换为字符串以便通过 URL 传递
        
        frontend_url = (
            f"http://localhost:5173/#/pages/login/login"  # 前端登录页地址
            f"?token={mc_uuid}"  # 传递 UUID
            f"&username={mc_name}"  # 传递用户名
            f"&whitelist={whitelist_str}"  # 传递白名单状态
        )
        return redirect(frontend_url)  # 重定向回前端
    

        
    except Exception as e:
        return f"认证失败: {str(e)}", 500  # 认证失败返回 500