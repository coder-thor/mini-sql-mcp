from abc import ABC, abstractmethod
from typing import Any

from jsonrpc import JSONRPCError, JSONRPCResponse


# 一种方法一条消息：initialize、ping、tools/list、tools/call
# 比如说 { id: xxx method: "tools/call", params: {} }
class Message(ABC):
    def __init__(self, id: str | int, params: dict[str, Any]) -> None:
        self.id = id
        self.params = params

    @abstractmethod
    def reply(self) -> JSONRPCResponse | JSONRPCError: ...
