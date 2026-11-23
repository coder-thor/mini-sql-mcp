from jsonrpc import JSONRPCResponse
from messages.base import Message
from tools import TOOLS


class ToolsList(Message):
    def reply(self) -> JSONRPCResponse:
        tools = []
        for tool in TOOLS.values():
            tools.append(tool.definition())
            # 最终这个 jsonresponse 里的 result 是什么样子？
            # { tools: [{ name: "get_artifact", input_schemas: {xx}, description: "xxx" }] }
        return JSONRPCResponse(jsonrpc="2.0", id=self.id, result={"tools": tools})
