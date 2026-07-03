// src/hooks/useChat.ts
import { useState } from "react";
import { getOrCreateThreadId } from "../utils/thread";
import { toUserFriendlyMessage } from "../utils/errorMessage";
import type { Message, ChatApiResponse } from "../types/chat";

const API_URL = `${import.meta.env.VITE_API_URL}/chat`;
const REQUEST_TIMEOUT_MS = 30000;

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

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const threadId = getOrCreateThreadId();
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content, thread_id: threadId }),
        signal: controller.signal,
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
      setError(toUserFriendlyMessage(err));
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  return { messages, sendMessage, loading, error };
}
