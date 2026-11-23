import logging

import uvicorn
from fastapi import FastAPI, Response
from fastapi import Request as HttpRequest

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

logger = logging.getLogger("http")


def json_reply(message: JSONRPCResponse | JSONRPCError) -> Response:
    line = message.model_dump_json()
    logger.info("send %s", line)
    # 返回 json对象
    return Response(line, status_code=200, media_type="application/json")


# streamablehttp
class HttpTransport(Transport):
    def serve(self) -> None:
        app = FastAPI()

        @app.post("/mcp")
        async def mcp(request: HttpRequest) -> Response:
            raw = (await request.body()).decode("utf-8", errors="replace")
            logger.info("recv %s", raw)
           # { id: xx, method: xx params: {xxx} }
            message = jsonrpc_message_adapter.validate_json(raw)
            logger.info("parsed %s", type(message).__name__)
            # 通知和别人发来的回复：官方这里回 202
            if not isinstance(message, JSONRPCRequest):
                return Response(status_code=202)
            try:
                reply = create_message(message).reply()
            except ProtocolError as caught:
                reply = failure(caught.id, caught.code, caught.message)
            return json_reply(reply)

        host, port = self.options.host, self.options.port
        logger.info("listening on http://%s:%d/mcp", host, port)
        uvicorn.run(app, host=host, port=port, log_config=None)
