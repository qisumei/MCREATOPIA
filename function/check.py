from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DB_PATH = "database.db"

def query_db(query, args=(), one=False):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv


@app.route("/query-range-blocks", methods=["GET"])
def query_range_blocks():
    try:
        x = int(request.args["x"])
        y = int(request.args["y"])
        z = int(request.args["z"])
        r = int(request.args["radius"])
        world = request.args["world"]

        level = query_db("SELECT id FROM levels WHERE name = ?", (world,), one=True)
        if not level:
            return jsonify([])

        world_id = level["id"]
        rows = query_db(
            "SELECT x,y,z,time,type,user,action FROM blocks "
            "WHERE level=? AND x BETWEEN ? AND ? AND y BETWEEN ? AND ? AND z BETWEEN ? AND ? "
            "ORDER BY time DESC LIMIT 100",
            (
                world_id,
                x - r, x + r,
                y - r, y + r,
                z - r, z + r
            )
        )

        result = []
        for row in rows:
            material = query_db("SELECT name FROM materials WHERE id=?", (row["type"],), one=True)
            user = query_db("SELECT name FROM users WHERE id=?", (row["user"],), one=True)

            result.append({
                "x": row["x"],
                "y": row["y"],
                "z": row["z"],
                "time": row["time"],
                "type": row["type"],
                "user": row["user"],
                "action": row["action"],
                "material": material["name"] if material else "未知材质",
                "username": user["name"] if user else "未知玩家"
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/query-blocks", methods=["GET"])
def query_blocks():
    try:
        x = int(request.args["x"])
        y = int(request.args["y"])
        z = int(request.args["z"])
        world = request.args["world"]

        level = query_db("SELECT id FROM levels WHERE name = ?", (world,), one=True)
        if not level:
            return jsonify([])

        world_id = level["id"]
        rows = query_db(
            "SELECT time,type,user,action FROM blocks WHERE level=? AND x=? AND y=? AND z=? ORDER BY time DESC",
            (world_id, x, y, z)
        )

        result = []
        for row in rows:
            material = query_db("SELECT name FROM materials WHERE id=?", (row["type"],), one=True)
            user = query_db("SELECT name FROM users WHERE id=?", (row["user"],), one=True)

            result.append({
                "time": row["time"],
                "type": row["type"],
                "user": row["user"],
                "action": row["action"],
                "material": material["name"] if material else "未知材质",
                "username": user["name"] if user else "未知玩家"
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "Block Query API running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=21004)
