// 手写 Streamable HTTP 客户端
// 零依赖：用 Node 自带的 fetch 发请求，自己解析 SSE

const ENDPOINT = "http://127.0.0.1:8000/mcp";

type SseEvent = { event: string; data: any };

type CallOptions = {
  signal?: AbortSignal;
  onProgress?: (progress: { done: number; total: number; message: string }) => void;
};

async function* readSse(body: ReadableStream<Uint8Array>): AsyncGenerator<SseEvent> {
  const decoder = new TextDecoder();
  let buffer = "";
  for await (const chunk of body) {
    buffer = (buffer + decoder.decode(chunk, { stream: true })).replace(/\r\n/g, "\n");
    let end: number;
    while ((end = buffer.indexOf("\n\n")) !== -1) {
      const block = buffer.slice(0, end);
      buffer = buffer.slice(end + 2);
      let event = "message";
      const data: string[] = [];
      for (const line of block.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
      }
      if (data.length) yield { event, data: JSON.parse(data.join("\n")) };
    }
  }
}

async function callTool(tool: string, args: Record<string, unknown>, options: CallOptions = {}): Promise<unknown> {
  console.log(`  → POST /mcp  ${JSON.stringify({ tool, arguments: args })}`);
  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
    },
    body: JSON.stringify({ tool, arguments: args }),
    signal: options.signal,
  });

  const contentType = res.headers.get("content-type") ?? "";
  console.log(`  ← HTTP ${res.status}  Content-Type: ${contentType}`);

  if (contentType.startsWith("application/json")) {
    const body = await res.json();
    if (!res.ok) throw new Error(body.error);
    return body.result;
  }

  if (contentType.startsWith("text/event-stream") && res.body) {
    for await (const { event, data } of readSse(res.body)) {
      if (event === "progress") options.onProgress?.(data);
      if (event === "result") return data;
    }
    throw new Error("SSE 流结束了，但没有收到结果");
  }

  throw new Error(`意外的响应：HTTP ${res.status} ${await res.text()}`);
}

function step(title: string) {
  console.log(`\n========== ${title} ==========`);
}

function printProgress(progress: { done: number; total: number; message: string }) {
  console.log(`  ⋯ ${progress.message}`);
}

async function demo() {
  step("1. 查 issue：快的，服务端直接回 JSON");
  console.log(await callTool("get_issue", { number: 42 }));

  step("2. 汇总 PR：慢的，服务端把这次回复变成 SSE 流");
  console.log(await callTool("summarize_prs", { months: 3 }, { onProgress: printProgress }));
}

async function demoCancel() {
  step("取消：收到两条进度后，客户端直接关掉这次的流");
  const controller = new AbortController();
  let received = 0;
  try {
    await callTool("summarize_prs", { months: 3 }, {
      signal: controller.signal,
      onProgress: (progress) => {
        printProgress(progress);
        if (++received === 2) controller.abort();
      },
    });
  } catch (error) {
    if ((error as Error).name !== "AbortError") throw error;
    console.log("  ✗ 流已关闭：关掉流本身就是取消，去看服务端日志");
  }
}

if (process.argv.includes("--cancel")) await demoCancel();
else await demo();
