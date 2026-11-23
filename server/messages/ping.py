from jsonrpc import JSONRPCResponse
from messages.base import Message


class Ping(Message):
    def reply(self) -> JSONRPCResponse:
        return JSONRPCResponse(jsonrpc="2.0", id=self.id, result={})
