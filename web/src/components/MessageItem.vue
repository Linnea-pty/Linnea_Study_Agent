<script setup lang="ts">
import { computed } from "vue";
import type { ChatMessage } from "../composables/useChat";
import { renderMarkdown } from "../utils/markdown";

const props = defineProps<{ message: ChatMessage; pending?: boolean }>();

const html = computed(() =>
  props.message.role === "assistant" ? renderMarkdown(props.message.content) : "",
);
</script>

<template>
  <article class="message" :class="message.role">
    <div class="avatar" aria-hidden="true">
      <span v-if="message.role === 'user'">你</span>
      <span v-else>L</span>
    </div>

    <div class="message-body">
      <p v-if="message.role === 'user'" class="user-text">{{ message.content }}</p>

      <template v-else>
        <div v-if="pending && !message.content" class="typing" aria-label="正在思考">
          <span></span><span></span><span></span>
        </div>
        <div v-else class="markdown" v-html="html"></div>
      </template>
    </div>
  </article>
</template>
