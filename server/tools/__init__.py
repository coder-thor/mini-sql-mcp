from tools.base import Tool
from tools.get_artifact import get_artifact
from tools.get_character import get_character
from tools.get_weapon import get_weapon

# 工具名 → 工具，写法和 transports/ 一样
TOOLS: dict[str, Tool] = {
    get_character.name: get_character,
    get_weapon.name: get_weapon,
    get_artifact.name: get_artifact,
}


def create_tool(name: str) -> Tool | None:
    return TOOLS.get(name)
