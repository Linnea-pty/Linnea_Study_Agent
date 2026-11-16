import { ref } from "vue";

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
}

interface DonePayload {
  reply: string;
  tier: string;
  session_id: string;
}

interface ServerEvent {
  event: string;
  data: Record<string, unknown>;
}

function parseEvent(raw: string): ServerEvent | null {
  let event = "message";
  const dataLines: string[] = [];
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trimStart());
  }
  if (dataLines.length === 0) return null;
  try {
    return { event, data: JSON.parse(dataLines.join("\n")) as Record<string, unknown> };
  } catch {
    return null;
  }
}

export function useChat() {
  const messages = ref<ChatMessage[]>([]);
  const sending = ref(false);
  const tier = ref("");
  const error = ref("");
  let nextId = 1;

  async function send(text: string): Promise<void> {
    const trimmed = text.trim();
    if (!trimmed || sending.value) return;

    error.value = "";
    messages.value.push({ id: nextId++, role: "user", content: trimmed });
    const reply: ChatMessage = { id: nextId++, role: "assistant", content: "" };
    messages.value.push(reply);
    sending.value = true;

    let finished = false;
    try {
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, session_id: "web" }),
      });
      if (!response.ok || !response.body) {
        throw new Error(`请求失败（HTTP ${response.status}）`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (!finished) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer = (buffer + decoder.decode(value, { stream: true })).replace(/\r\n/g, "\n");
        const blocks = buffer.split("\n\n");
        buffer = blocks.pop() ?? "";

        for (const block of blocks) {
          const parsed = parseEvent(block);
          if (!parsed) continue;
          if (parsed.event === "done") {
            const payload = parsed.data as unknown as DonePayload;
            reply.content = payload.reply || "（本轮没有返回内容，请重试。）";
            tier.value = payload.tier || "";
            finished = true;
            break;
          }
          if (parsed.event === "error") {
            throw new Error(String(parsed.data.message ?? "服务端处理失败"));
          }
        }
      }

      if (!finished && !reply.content) {
        throw new Error("连接提前结束，没有收到回答。");
      }
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : String(cause);
      error.value = message;
      reply.content = reply.content || "抱歉，这一轮出错了，请稍后重试。";
    } finally {
      sending.value = false;
    }
  }

  function clear(): void {
    messages.value = [];
    tier.value = "";
    error.value = "";
  }

  async function restore(): Promise<void> {
    try {
      const response = await fetch("/api/history/web");
      if (!response.ok) return;
      const data = (await response.json()) as {
        messages?: Array<{ role: string; content: string }>;
      };
      if (!data.messages?.length) return;
      messages.value = data.messages.map((item) => ({
        id: nextId++,
        role: item.role === "assistant" ? "assistant" : "user",
        content: item.content,
      }));
    } catch {
      // 历史读取失败不应阻断新对话
    }
  }

  return { messages, sending, tier, error, send, clear, restore };
}
