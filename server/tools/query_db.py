from typing import Annotated

from pydantic import Field

from db import QueryError, read
from tools.base import tool


# 新增的和数据库交互的tool 

@tool
def query_db(sql: Annotated[str, Field(description="一条 SELECT、WITH 或 EXPLAIN")]) -> list:
    """执行一条只读 SQL，最多返回 100 行。"""
    try:
        return read(sql)
    except QueryError as caught:
        return [{"error": str(caught)}]
