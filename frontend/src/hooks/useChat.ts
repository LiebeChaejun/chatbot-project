// src/hooks/useChat.ts
import { useState } from "react";
import { getOrCreateThreadId } from "../utils/thread";
import type { Message, ChatApiResponse } from "../types/chat";

const API_URL = `${import.meta.env.VITE_API_URL}/chat`;

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const threadId = getOrCreateThreadId();
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content, thread_id: threadId }),
      });

      const data: ChatApiResponse = await res.json();

      if (!res.ok || "error" in data) {
        const message =
          "error" in data ? data.error : `서버오류: ${res.status}`;
        throw new Error(message);
      }

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "알 수 없는 오류가 발생했어요."
      );
    } finally {
      setLoading(false);
    }
  };

  return { messages, sendMessage, loading, error };
}
