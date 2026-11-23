from jsonrpc import JSONRPCResponse
from messages.base import Message

PROTOCOL_VERSION = "2025-11-25"
SERVER_INFO = {"name": "mini-sql-mcp", "version": "0.1.0"}


class Initialize(Message):
    def reply(self) -> JSONRPCResponse:
        return JSONRPCResponse(jsonrpc="2.0", id=self.id, result={
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })
