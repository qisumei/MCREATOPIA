import sqlite3  # 导入 sqlite3 用于操作 SQLite 数据库
from flask import g, current_app  # 导入 Flask 全局对象 g 和 current_app 用于访问应用配置

def get_db():
    """获取数据库连接并缓存到 Flask 的 g 对象中"""
    if 'db' not in g:  # 如果 g 中尚未存在数据库连接则创建一个
        # 从应用配置中读取数据库路径
        db_path = current_app.config['DB_PATH']  # 从 current_app 配置中读取 DB_PATH
        db_uri = f"file:{db_path}?mode=ro"  # 使用只读模式构建 URI，避免应用修改数据库
        g.db = sqlite3.connect(db_uri, uri=True)  # 通过 URI 连接到 SQLite 数据库并保存到 g.db
        g.db.row_factory = sqlite3.Row  # 将返回的行设为 sqlite3.Row，以便按列名访问
    return g.db  # 返回缓存的数据库连接

def query_db(query, args=(), one=False):
    """执行查询并返回结果：默认返回所有行，可通过 one=True 返回单行或 None"""
    try:
        db = get_db()  # 获取（或创建）数据库连接
        cur = db.execute(query, args)  # 执行 SQL 查询，支持参数化的 args
        rv = cur.fetchall()  # 获取所有结果行
        return (rv[0] if rv else None) if one else rv  # 根据 one 参数返回第一条或全部
    except sqlite3.Error as e:
        print(f"Database error: {e}")  # 出错时打印错误信息到控制台
        return None  # 出现数据库错误时返回 None

def close_db(e=None):
    """在应用上下文结束时关闭并移除 g 中的数据库连接"""
    db = g.pop('db', None)  # 从 g 中弹出 db（如果存在），pop 保证不会抛出 KeyError
    if db is not None:  # 如果确实存在数据库连接，则关闭它
        db.close()  # 关闭连接，释放资源