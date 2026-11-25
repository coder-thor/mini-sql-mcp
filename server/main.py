import argparse
from pathlib import Path

from logger import setup_logging

setup_logging()

import tools  # noqa: F401
from app import mcp
from db import configure


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only SQLite MCP server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--db", default=str(Path(__file__).parent / "demo.sqlite"))
    args = parser.parse_args()
    configure(args.db)

    if args.transport == "stdio":
        mcp.run("stdio")
    else:
        mcp.run("streamable-http", host=args.host, port=args.port)

# stdio模式最明显的特征就是 它自己不会启动 它在等谁拉他 父进程 ai agent

if __name__ == "__main__":
    main()

# cursor最终走的是uv run main.py
