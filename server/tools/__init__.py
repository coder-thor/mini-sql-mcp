from tools.base import Tool
from tools.query_db import query_db

# 工具名 → 工具，写法和 transports/ 一样
TOOLS: dict[str, Tool] = {
    query_db.name: query_db,
}


def create_tool(name: str) -> Tool | None:
    return TOOLS.get(name)
