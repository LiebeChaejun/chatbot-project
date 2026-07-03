// localStorage 키
export const STORAGE_KEYS = {
  THREAD_ID: "chat_thread_id",
} as const;

// API 관련
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL,
  CHAT_ENDPOINT: "/chat",
  TIMEOUT_MS: 30000,
} as const;
