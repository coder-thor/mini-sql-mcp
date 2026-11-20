import asyncio
import logging

import uvicorn
from fastapi import FastAPI, Request, Response

from transports.base import Transport

logger = logging.getLogger("http")

LOGGED_HEADERS = ("user-agent", "accept", "content-type", "mcp-protocol-version", "mcp-session-id")

# streamablehttp 
class HttpTransport(Transport):
    def serve(self) -> None:
        app = FastAPI()

        @app.api_route("/mcp", methods=["GET", "POST", "DELETE"])
        async def mcp(request: Request) -> Response:
            headers = {name: request.headers[name] for name in LOGGED_HEADERS if name in request.headers}
            body = (await request.body()).decode("utf-8", errors="replace")
            logger.info("%s /mcp headers=%s", request.method, headers)
            logger.info("%s /mcp body=%s", request.method, body)
            while not await request.is_disconnected():
                await asyncio.sleep(1)
            logger.info("%s /mcp client disconnected", request.method)
            return Response()

        host, port = self.options.host, self.options.port
        logger.info("listening on http://%s:%d/mcp", host, port)
        uvicorn.run(app, host=host, port=port, log_config=None)
