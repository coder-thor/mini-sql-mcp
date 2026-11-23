from typing import Annotated

from pydantic import Field

from tools.base import tool


@tool
def get_character(name: Annotated[str, Field(description="角色的中文名")]) -> list:
    """查角色的星级、元素、武器类型"""
    return []
