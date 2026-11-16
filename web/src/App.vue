<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue";
import MessageItem from "./components/MessageItem.vue";
import { useChat } from "./composables/useChat";

const { messages, sending, tier, error, send, clear, restore } = useChat();

const draft = ref("");
const scroller = ref<HTMLElement | null>(null);
const textarea = ref<HTMLTextAreaElement | null>(null);

const suggestions = [
  "帮我看看这道 PTA 题",
  "解释一下什么是闭包",
  "找几篇关于 RAG 的论文",
  "用 Python 写一个快速排序",
];

const tierLabel = computed(() => {
  if (tier.value === "balanced") return "增强推理";
  if (tier.value === "fast") return "快速响应";
  return "";
});

const lastAssistant = computed(() =>
  [...messages.value].reverse().find((message) => message.role === "assistant"),
);

function scrollToBottom(): void {
  void nextTick(() => {
    scroller.value?.scrollTo({ top: scroller.value.scrollHeight, behavior: "smooth" });
  });
}

function resize(): void {
  const element = textarea.value;
  if (!element) return;
  element.style.height = "auto";
  element.style.height = `${Math.min(element.scrollHeight, 168)}px`;
}

async function submit(): Promise<void> {
  const text = draft.value.trim();
  if (!text || sending.value) return;
  draft.value = "";
  await nextTick();
  resize();
  scrollToBottom();
  await send(text);
  scrollToBottom();
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    void submit();
  }
}

function useSuggestion(text: string): void {
  draft.value = text;
  void nextTick(() => {
    resize();
    textarea.value?.focus();
  });
}

function startNew(): void {
  if (sending.value) return;
  clear();
  draft.value = "";
  void nextTick(() => {
    resize();
    textarea.value?.focus();
  });
}

watch(() => messages.value.map((message) => message.content.length).join(","), scrollToBottom);
watch(draft, () => void nextTick(resize));
onMounted(() => {
  textarea.value?.focus();
  void restore();
});
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">
          <svg viewBox="0 0 32 32" aria-hidden="true">
            <path d="M16 27C16 18 21 12 28 10c-1 9-5 16-12 17Z" fill="#a8d5bd" />
            <path
              d="M16 27C18 20 21 16 26 13"
              stroke="#e8efe9"
              stroke-width="1.3"
              stroke-linecap="round"
            />
          </svg>
        </div>
        <div>
          <p class="brand-name">Linnea</p>
          <p class="brand-sub">学习助手</p>
        </div>
      </div>

      <button class="new-chat" type="button" @click="startNew">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 5v14M5 12h14" />
        </svg>
        新对话
      </button>

      <div class="sidebar-block">
        <p class="sidebar-label">工作区</p>
        <ul class="capabilities">
          <li><span class="cap-dot mint"></span>网页题目识别</li>
          <li><span class="cap-dot gold"></span>学术检索</li>
          <li><span class="cap-dot blue"></span>代码与计算</li>
        </ul>
      </div>

      <div class="sidebar-note">
        <p class="sidebar-label">最近</p>
        <p class="empty-note">对话保存在本地，随时续聊。</p>
      </div>

      <div class="sidebar-foot">
        <span class="live-dot"></span>
        <span>本地运行 · 数据不离开设备</span>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div class="topbar-copy">
          <p class="eyebrow">PERSONAL STUDY AGENT</p>
          <h1>和 Linnea 一起学习</h1>
        </div>
        <div class="topbar-actions">
          <span v-if="tierLabel" class="tier-pill">{{ tierLabel }}</span>
          <button class="ghost" type="button" @click="startNew">清空</button>
        </div>
      </header>

      <section ref="scroller" class="messages" aria-live="polite">
        <div v-if="messages.length === 0" class="empty">
          <div class="empty-orb" aria-hidden="true">
            <svg viewBox="0 0 32 32">
              <path d="M16 27C16 18 21 12 28 10c-1 9-5 16-12 17Z" fill="#dff0e6" />
              <path
                d="M16 27C18 20 21 16 26 13"
                stroke="#245c46"
                stroke-width="1.1"
                stroke-linecap="round"
              />
            </svg>
          </div>
          <h2>今天想学点什么？</h2>
          <p class="lede">贴一道题、丢一个链接，或者直接问一个概念。<br />剩下的交给我。</p>
          <div class="suggestions">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion"
              type="button"
              class="suggestion"
              @click="useSuggestion(suggestion)"
            >
              <span>{{ suggestion }}</span>
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </button>
          </div>
        </div>

        <div v-else class="thread">
          <MessageItem
            v-for="message in messages"
            :key="message.id"
            :message="message"
            :pending="sending && message.id === lastAssistant?.id"
          />
        </div>
      </section>

      <footer class="composer-wrap">
        <Transition name="toast">
          <p v-if="error" class="error-toast">{{ error }}</p>
        </Transition>
        <div class="composer" :class="{ busy: sending }">
          <textarea
            ref="textarea"
            v-model="draft"
            rows="1"
            placeholder="输入问题，或粘贴题目链接…"
            :disabled="sending"
            @keydown="onKeydown"
          ></textarea>
          <button
            class="send"
            type="button"
            :disabled="!draft.trim() || sending"
            aria-label="发送"
            @click="submit"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 19V5M6 11l6-6 6 6" />
            </svg>
          </button>
        </div>
        <p class="hint">Enter 发送 · Shift + Enter 换行 · 回答仅供学习参考</p>
      </footer>
    </main>
  </div>
</template>
