# 导入即注册：模块里的 @mcp.tool() 在 import 时把函数挂到 mcp 上，新工具在这里加一行
from tools import query_db  # noqa: F401
