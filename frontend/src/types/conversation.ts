import type { Message } from "./chat";

export interface Conversation {
  threadId: string;
  title: string;
  createdAt: string;
  updatedAt: string;
}

interface RawMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ConversationMessagesResponse {
  threadId: string;
  message: RawMessage[];
}
