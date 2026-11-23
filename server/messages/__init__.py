import logging

from jsonrpc import METHOD_NOT_FOUND, JSONRPCRequest, ProtocolError
from messages.base import Message
from messages.initialize import Initialize
from messages.ping import Ping
from messages.tools_call import ToolsCall
from messages.tools_list import ToolsList

logger = logging.getLogger("messages")

# 方法名 → 消息类，写法和 transports/ 一样
MESSAGES: dict[str, type[Message]] = {
    "initialize": Initialize,
    "ping": Ping,
    "tools/list": ToolsList,
    "tools/call": ToolsCall,
}


def create_message(request: JSONRPCRequest) -> Message:
    logger.info("dispatch %s id=%s", request.method, request.id)
    # { id: xx, method: "initiliaze / tools/call"  }
    cls = MESSAGES.get(request.method)
    if cls is None:
        raise ProtocolError(METHOD_NOT_FOUND, f"Method not found: {request.method}", request.id)
    return cls(request.id, request.params or {})
