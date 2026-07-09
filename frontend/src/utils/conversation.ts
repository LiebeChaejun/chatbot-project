import type { Message } from "../types/chat";
import type {
  Conversation,
  ConversationMessagesResponse,
} from "../types/conversation";

interface RawConversation {
  thread_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export function toConversation(raw: RawConversation): Conversation {
  return {
    threadId: raw.thread_id,
    title: raw.title,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  };
}

export function toConversations(rawList: RawConversation[]): Conversation[] {
  return rawList.map(toConversation);
}

export function toMessages(response: ConversationMessagesResponse): Message[] {
  return response.message.map((raw) => ({
    id: crypto.randomUUID(),
    role: raw.role,
    content: raw.content,
  }));
}
