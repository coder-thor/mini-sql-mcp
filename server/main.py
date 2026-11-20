import argparse

from logger import setup_logging
from transports import TRANSPORTS, TransportOptions, create_transport


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only SQLite MCP server")
    parser.add_argument("--transport", choices=list(TRANSPORTS), default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    # 面对这种多分支语句我们到底要怎么拆， 开闭原则
    # 如果一个函数的内容已经固定写完了就要进来避免对齐进行更改 因为一个函数可能会被很多地方调用 foo a b c d
    # 函数体是 immutable 不可变更

    setup_logging()
    options = TransportOptions(host=args.host, port=args.port)
    # 造车工厂 奔驰 宝马 特斯拉
    create_transport(args.transport, options).serve()

# stdio模式最明显的特征就是 它自己不会启动 它在等谁拉他 父进程 ai agent

if __name__ == "__main__":
    main()

# cursor最终走的是uv run main.py