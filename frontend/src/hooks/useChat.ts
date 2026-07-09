import { useState, useEffect } from "react";
import { API_CONFIG } from "../constants";
import { toUserFriendlyMessage } from "../utils/errorMessage";
import { toMessages } from "../utils/conversation";
import type { Message } from "../types/chat";
import type { ChatApiResponse } from "../types/api";
import type { ConversationMessagesResponse } from "../types/conversation";

export function useChat(threadId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!threadId) {
      setMessages([]);
      return;
    }
    const loadPastMessages = async () => {
      try {
        const res = await fetch(
          `${API_CONFIG.BASE_URL}/conversations/${threadId}/ messages`
        );
        if (!res.ok) {
          setMessages([]);
          return;
        }
        const data: ConversationMessagesResponse = await res.json();
        setMessages(toMessages(data));
      } catch {
        setMessages([]);
      }
    };

    loadPastMessages();
  }, [threadId]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || !threadId) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      API_CONFIG.TIMEOUT_MS
    );

    try {
      const res = await fetch(`${API_CONFIG.BASE_URL}/chat`, {
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
