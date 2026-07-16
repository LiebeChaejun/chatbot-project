import { useState, useEffect } from "react";
import { API_CONFIG } from "../constants";
import { toConversations, toConversation } from "../utils/conversation";
import { toUserFriendlyMessage } from "../utils/errorMessage";
import type { Conversation } from "../types/conversation";

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchConversations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_CONFIG.BASE_URL}/conversations`);
      if (!res.ok) throw new Error("대화 목록을 불러오지 못했어요.");

      const data = await res.json();
      setConversations(toConversations(data.conversations));
    } catch (err) {
      setError(toUserFriendlyMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  const createConversation = async (): Promise<Conversation | null> => {
    setError(null);
    try {
      const res = await fetch(`${API_CONFIG.BASE_URL}/conversations`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("새 대화를 생성하지 못했어요.");

      const data = await res.json();
      const conversation = toConversation(data);

      setConversations((prev) => [conversation, ...prev]);
      return conversation;
    } catch (err) {
      setError(toUserFriendlyMessage(err));
      return null;
    }
  };

  const renameConversation = async (threadId: string, title: string) => {
    setError(null);

    try {
      const res = await fetch(
        `${API_CONFIG.BASE_URL}/conversations/${threadId}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title }),
        }
      );
      if (!res.ok) throw new Error("제목을 수정하지 못했어요.");

      setConversations((prev) =>
        prev.map((c) => (c.threadId === threadId ? { ...c, title } : c))
      );
    } catch (err) {
      setError(toUserFriendlyMessage(err));
    }
  };

  const touchConversation = (threadId: string) => {
    setConversations((prev) => {
      const target = prev.find((c) => c.threadId === threadId);
      if (!target) return prev;
      const rest = prev.filter((c) => c.threadId !== threadId);
      return [{ ...target, updatedAt: new Date().toISOString() }, ...rest];
    });
  };

  const clearError = () => setError(null);

  return {
    conversations,
    loading,
    error,
    createConversation,
    renameConversation,
    touchConversation,
    refreshConversations: fetchConversations,
    clearError,
  };
}
