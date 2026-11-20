import logging
from pathlib import Path

LOG_FILE = Path(__file__).parent / "log.txt"


def setup_logging() -> None:
    # stdout is reserved for protocol messages under the stdio transport
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s pid=%(process)d] %(message)s",
        encoding="utf-8",
    )
