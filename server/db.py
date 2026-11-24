import logging
import sqlite3
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger("db")

# 工具执行失败：语句不合法，或 SQLite 报错。回给模型，不走 JSON-RPC error。
class QueryError(Exception):
    pass


_PATH: str | None = None
_ALLOWED = {"SELECT", "WITH", "EXPLAIN"}
_LIMIT = 100


def configure(path: str) -> None:
    # sqlite是轻量的数据库库 通常以单个文件的形式存在， 会用于企业服务中的sidecar 服务或者是移动端手机 app 的本地数据库
    file = Path(path).expanduser().resolve()
    if not file.is_file():
        raise SystemExit(f"数据库不存在: {file}")
    global _PATH # global 代表要使用全局变量的_PATH
    _PATH = str(file)
    logger.info("open %s", _PATH)

# 后续 ai 经过 sqlite mcp 调用的所有 sql 都会先到这个 fetch 函数里来对吧
# 然后由fetch函数去对sqlite进行真正的操作
def fetch(sql: str, params: tuple = ()) -> list[dict]:
    if _PATH is None:
        raise QueryError("数据库还没打开")
    # mode=ro 是文件锁，query_only 是连接锁。模型写出 INSERT 也落不了盘。
    uri = "file:" + quote(_PATH, safe="/") + "?mode=ro"
    connection = None
    try:
        # 连接本地sqlite数据库文件
        connection = sqlite3.connect(uri, uri=True)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        # 执行你给的sql
        logger.info("execute %s", sql)
        cursor = connection.execute(sql, params)
        rows = [dict(row) for row in cursor.fetchmany(_LIMIT + 1)]
    except sqlite3.Error as caught:
        raise QueryError(str(caught)) from caught
    finally:
        if connection is not None:
            connection.close()
    return rows[:_LIMIT]


# 只读sql
def readonly(sql: str) -> str:
    # 不用 startswith("SELECT")：WITH 会被拒绝，SELECT 1; DROP TABLE 会被放过。
    text = sql.strip()
    if not text:
        raise QueryError("SQL 为空")
    if "--" in text or "/*" in text:
        raise QueryError("不支持注释")
    if text.endswith(";"):
        text = text[:-1].rstrip()
    if ";" in text:
        raise QueryError("只允许一条语句")
    word = text.split(None, 1)[0].upper()
    if word not in _ALLOWED:
        raise QueryError("只允许 SELECT、WITH 或 EXPLAIN")
    return text


def read(sql: str) -> list[dict]:
    return fetch(readonly(sql))
