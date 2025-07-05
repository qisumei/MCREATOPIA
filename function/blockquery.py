import datetime
import aiohttp
import logging

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 世界映射
WORLD_NAME_MAP = {
    "主世界": "minecraft:overworld",
    "末地": "minecraft:the_end",
    "下界": "minecraft:the_nether"
}

# 动作映射
ACTION_MAP = {
    0: "破坏",
    1: "放置",
    2: "使用"
}

class BlockQuery:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url

    async def query_block(self, world_ch: str, mode: str, x: int, y: int, z: int, radius: int = None) -> str:
        try:
            world_id = WORLD_NAME_MAP.get(world_ch)
            if not world_id:
                return f"未知世界：{world_ch}"

            async with aiohttp.ClientSession() as session:
                if mode == '具体':
                    params = {"x": x, "y": y, "z": z, "world": world_id}
                    async with session.get(f"{self.api_base_url}/query-blocks", params=params) as resp:
                        if resp.status != 200:
                            return f"API 查询失败: {resp.status}"
                        data = await resp.json()

                    if not data:
                        return f"在坐标 ({x},{y},{z}) 未找到任何方块记录。"

                    lines = [f"📋 坐标 ({x},{y},{z}) 历史记录（共{len(data)}条）："]
                    for r in data:
                        dt = datetime.datetime.fromtimestamp(r['time'] / 1000)
                        action_desc = ACTION_MAP.get(r['action'], f"未知({r['action']})")
                        lines.append(
                            f"[{dt:%Y-%m-%d %H:%M:%S}] {r['material']} — 玩家 {r['username']} — 动作: {action_desc}"
                        )
                    return "\n".join(lines)

                elif mode == '范围':
                    if radius is None:
                        return "范围查询需要指定半径，例如：…,(radius)"

                    params = {"x": x, "y": y, "z": z, "radius": radius, "world": world_id}
                    async with session.get(f"{self.api_base_url}/query-range-blocks", params=params) as resp:
                        if resp.status != 200:
                            return f"API 查询失败: {resp.status}"
                        data = await resp.json()

                    if not data:
                        return f"在范围 ±{radius} 内未找到任何方块记录。"

                    lines = [f"🔍 范围查询 ({x},{y},{z}) ±{radius} 共{len(data)}条："]
                    for r in data:
                        dt = datetime.datetime.fromtimestamp(r['time'] / 1000)
                        action_desc = ACTION_MAP.get(r['action'], f"未知({r['action']})")
                        lines.append(
                            f"[{dt:%Y-%m-%d %H:%M:%S}] 坐标({r['x']},{r['y']},{r['z']}) — "
                            f"{r['material']} — 玩家 {r['username']} — 动作: {action_desc}"
                        )
                    return "\n".join(lines)
                else:
                    return "无效的查询模式，请使用 '具体' 或 '范围'。"

        except Exception as e:
            logger.exception("查询方块信息时出错")
            return "查询执行失败，请检查日志。"
