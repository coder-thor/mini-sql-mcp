import logging

# mcp就是我们要用到的官方 sdk
from mcp.server import MCPServer

logger = logging.getLogger("messages")


# 协议层交给 SDK 之后，收发日志靠 middleware 补：每个请求和通知都会经过这里
async def log_requests(ctx, call_next):
    logger.info("dispatch %s id=%s params=%s", ctx.method, ctx.request_id, ctx.params)
    try:
        result = await call_next(ctx)
    except Exception as caught:
        logger.warning("dispatch %s id=%s failed: %r", ctx.method, ctx.request_id, caught)
        raise
    logger.info("reply %s id=%s -> %s", ctx.method, ctx.request_id, result)
    return result


mcp = MCPServer("mini-sql-mcp", version="0.1.0", middleware=[log_requests])
