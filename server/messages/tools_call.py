import json

from jsonrpc import INVALID_PARAMS, JSONRPCError, JSONRPCResponse, failure
from messages.base import Message
from tools import create_tool


class ToolsCall(Message):
    def reply(self) -> JSONRPCResponse | JSONRPCError:
        name = self.params.get("name") # 要调用的 tool 的 name
        # tool: 就是Tool 的实例
        tool = create_tool(name) if isinstance(name, str) else None # tool = create_tool 可以拿到类似  get_character 这样的函数， 而这个函数是不是被装饰器给装饰过的 Tool( get_character)
        if tool is None:
            return failure(self.id, INVALID_PARAMS, f"Unknown tool: {name}")
        arguments = self.params.get("arguments") or {}
        # tool(arguments) 调用工具 实际上就是在调用__call__, __call__内部就会验证参数并且调用真正的那个 tool
        text = json.dumps(tool(arguments), ensure_ascii=False) # 转成json字符串
        body = {"content": [{"type": "text", "text": text}], "isError": False}
        return JSONRPCResponse(jsonrpc="2.0", id=self.id, result=body)


# 最先由 stdio或者 streamablehttp 的入口捕捉到对应的请求信息并进行处理
# 然后将合法的{ id: xx method: xxx } 这样的JSONRPCREQUEST 消息提交给 message工厂去匹配
# tools/call 就能匹配到对应的ToolsCall这个类， 然后类上面的 reply 方法会在实例化以后被调用 ， 然后每个 message 类的 reply 都不一样
# tools/call作为最复杂的会去解析参数然后调用对应的 create_tool tool里又是去找对应的tools工厂对吧
# 然后tools 工厂里的每个tool都被@tool 装饰过了 所以每个tool 都是Tool(fn)这样的实例
# tool(arguments) 实际上就是在调用对应的tool.__call__(arguments)
# __call__里会去调用真正的 fn