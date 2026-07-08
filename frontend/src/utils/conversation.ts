import type { Message } from "../types/chat";
import type { ConversationMessagesResponse } from "../types/conversation";

export function toMessages(response: ConversationMessagesResponse): Message[] {
  return response.messages.map((raw) => ({
    id: crypto.randomUUID(),
    role: raw.role,
    content: raw.content,
  }));
}
