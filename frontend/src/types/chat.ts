// src/types/chat.ts
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export interface ChatApiResponse {
  response?: string;
  error?: string;
}
