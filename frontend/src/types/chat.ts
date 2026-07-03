// src/types/chat.ts
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export type ChatApiResponse =
  | { response: string; error?: never }
  | { error: string; response?: never };
