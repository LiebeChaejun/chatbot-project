// src/utils/thread.ts
const THREAD_ID_KEY = "chat_thread_id";

export function getOrCreateThreadId(): string {
  let threadId = localStorage.getItem(THREAD_ID_KEY);
  if (!threadId) {
    threadId = crypto.randomUUID();
    localStorage.setItem(THREAD_ID_KEY, threadId);
  }
  return threadId;
}
