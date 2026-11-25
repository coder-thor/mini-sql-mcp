from typing import Annotated

from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from app import mcp
from db import QueryError, read


@mcp.tool()
def query_db(sql: Annotated[str, Field(description="一条 SELECT、WITH 或 EXPLAIN")]) -> list[dict]:
    """执行一条只读 SQL，最多返回 100 行。"""
    try:
        return read(sql)
    except QueryError as caught:
        raise ToolError(str(caught)) from caught
