from typing import Annotated

from pydantic import Field

from tools.base import tool


@tool
def get_weapon(name: Annotated[str, Field(description="角色的中文名")]) -> list:
    """查角色的推荐武器"""
    return []
