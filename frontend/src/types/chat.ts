// src/types/chat.ts
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export interface Res {
  threadId: string;
  message: Message[];
}
