import asyncio
import json
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

app = FastAPI()


@dataclass
class Progress:
    done: int
    total: int
    message: str

# #42 issue的具体内容
FAKE_ISSUES = {
    42: {"title": "登录页偶发 500", "state": "open", "author": "octocat", "comments": 7},
}


async def get_issue(arguments: dict[str, Any]) -> dict[str, Any]:
    number = arguments.get("number")
    issue = FAKE_ISSUES.get(number)
    if issue is None:
        return {"error": f"找不到 issue #{number}"}
    return {"number": number, **issue}


# mock 模拟一段数据
async def summarize_prs(arguments: dict[str, Any]) -> AsyncIterator[Progress | dict[str, Any]]:
    months = arguments.get("months", 3) # 后续读取三个月的pr的时候会进入这个函数
    total = 450 # mock 最大 pr 数
    # for in 后面的跟的是什么 可迭代对象 iterator yield 迭代接口， for in "str" for in array const str = "hello" console.log(str.__iterator__)
    for done in range(50, total + 1, 50): # range 从 50 开始，  100 150  451  450  9词
        await asyncio.sleep(0.6) # 等0.6秒
        # 100 
        # 150
        yield Progress(done, total, f"已读 {done} / {total} 个 PR") # 让出9 次  第一次让出已经回来了 
    yield {"summary": f"最近 {months} 个月合进 main 的 {total} 个 PR：功能 210 个，修复 180 个，其他 60 个"}

# asyncwith代码块结束的时候 会让出结束 就是会把函数主导权交回来
# for in 每次 for in的代码块结束 就代表让出结束，就会回到原函数

@dataclass
class Tool:
    handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]] | Callable[[dict[str, Any]], AsyncIterator[Any]]
    streaming: bool


TOOLS = {
    # 是否是长任务sse 都是服务端决定的
    "get_issue": Tool(handler=get_issue, streaming=False),
    "summarize_prs": Tool(handler=summarize_prs, streaming=True), # 这个streaming = true 就是长时间要处理的任务
}


# 返回一个字符串`` sse响应的标准格式
def sse_event(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/mcp") # post /mcp
async def mcp_endpoint(request: Request) -> Response:
    body = await request.json() # { tool: "xxx", "arguments": { number: 42 } }
    name = body.get("tool") # get_issue summarize_prs
    arguments = body.get("arguments") or {} # get_weaponse
    tool = TOOLS.get(name)
    if tool is None:
        return JSONResponse({"error": f"未知工具：{name}"}, status_code=404)

    if not tool.streaming: # 如果不是长任务 那就直接返回 json
        print(f"[server] {name}：直接回 JSON")
        return JSONResponse({"result": await tool.handler(arguments)})

    # 本质上 streamablehttp呢就是服务端做的一次 if else 
    print(f"[server] {name}：这次回复改成 SSE 流")
    # 这个 streaming response 里面也有 forin 
    # 100 
    return StreamingResponse(
        stream_tool_call(name, tool, arguments),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def stream_tool_call(name: str, tool: Tool, arguments: dict[str, Any]) -> AsyncIterator[str]:
    try:
        # stream pr summarize_prs

    # mock 模拟一段数据
    # async def summarize_prs(arguments: dict[str, Any]) -> AsyncIterator[Progress | dict[str, Any]]:
    #     months = arguments.get("months", 3) # 后续读取三个月的pr的时候会进入这个函数
    #     total = 450 # mock 最大 pr 数
    #     # for in 后面的跟的是什么 可迭代对象 iterator yield 迭代接口， for in "str" for in array const str = "hello" console.log(str.__iterator__)
    #     for done in range(50, total + 1, 50): # range 从 50 开始，  100 150  451  450  9词
    #         await asyncio.sleep(0.6) # 等0.6秒
    #         yield Progress(done, total, f"已读 {done} / {total} 个 PR") # 让出9 次  
    #     yield {"summary": f"最近 {months} 个月合进 main 的 {total} 个 PR：功能 210 个，修复 180 个，其他 60 个"}

    # # asyncwith代码块结束的时候 会让出结束 就是会把函数主导权交回来
    # # for in 每次 for in的代码块结束 就代表让出结束，就会回到原函数

        async for item in tool.handler(arguments):
            # item 第一次的值 是 Progress(50, 450, f"已读 {done} / {total} 个 PR")
            # 第二次的值 Progress(100， total, f"已读 {done} / {total} 个 PR")
            if isinstance(item, Progress):
                print(f"[server] {name} 推进度：{item.message}")
                yield sse_event("progress", {"done": item.done, "total": item.total, "message": item.message})
            else:
                print(f"[server] {name} 推最终结果，关闭流")
                yield sse_event("result", item)
    except asyncio.CancelledError:
        print(f"[server] {name}：客户端关掉了流，等于取消请求，停止干活")
        raise


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
