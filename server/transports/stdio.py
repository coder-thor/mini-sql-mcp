import logging
import sys

from jsonrpc import (
    JSONRPCError,
    JSONRPCRequest,
    JSONRPCResponse,
    ProtocolError,
    failure,
    jsonrpc_message_adapter,
)
from messages import create_message
from transports.base import Transport

logger = logging.getLogger("stdio")


class StdioTransport(Transport):
    def serve(self) -> None:
        logger.info("started argv=%s", sys.argv)
        # 监听父进程的 stdin 消息 一直在迭代
        for raw in sys.stdin:
            line = raw.strip() # { id: xx method: xxx }\n
            if not line: # if !line line在 strip 以后还有没有值
                continue
            logger.info("recv %s", line)
            # 基于pydantic 去确认传过来的message是合法的调用
            # { id: xx, method:xx, params: {}, jsonrpc: 2.0 }
            message = jsonrpc_message_adapter.validate_json(line)
            logger.info("parsed %s", type(message).__name__)
            # 通知和别人发来的回复都没有要我们答的请求
            # JSONRPCNOTIFICATION
            if not isinstance(message, JSONRPCRequest):
                continue
            try:
                # { id: xx, result: { xxx } } 
                # 如果是合法的 request对象
                reply = create_message(message).reply() #得到工具调用结果 getcharacter 
            except ProtocolError as caught:
                reply = failure(caught.id, caught.code, caught.message)
            self.send(reply)
        logger.info("stdin closed, exiting")

    # stdout 只能写协议消息，一条一行
    def send(self, message: JSONRPCResponse | JSONRPCError) -> None:
        line = message.model_dump_json()
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        logger.info("send %s", line)
