export const STORAGE_KEYS = {
  LAST_THREAD_ID: "chat_last_thread_id",
} as const;

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL,
  TIMEOUT_MS: 30000,
} as const;

export const TITLE_MAX_LENGTH = 20;
