import logging
import sys

from transports.base import Transport

logger = logging.getLogger("stdio")


class StdioTransport(Transport):
    def serve(self) -> None:
        logger.info("started argv=%s", sys.argv)
        # 监听父进程的 stdin 消息 一直在迭代
        for line in sys.stdin:
            logger.info("recv %s", line.rstrip("\n"))
        logger.info("stdin closed, exiting")
