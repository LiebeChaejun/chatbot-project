import { STORAGE_KEYS } from "../constants";

export function getOrCreateThreadId(): string {
  let threadId = localStorage.getItem(STORAGE_KEYS.THREAD_ID);
  if (!threadId) {
    threadId = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEYS.THREAD_ID, threadId);
  }
  return threadId;
}
