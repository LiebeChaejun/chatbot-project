// src/components/ChatWindow.tsx
import { useEffect, useRef } from "react";
import type { Message } from "../types/chat";
import { MessageBubble } from "./MessageBubble";

interface Props {
  messages: Message[];
  loading: boolean;
}

export function ChatWindow({ messages, loading }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {loading && <div className="text-gray-400 text-sm">답변 작성 중...</div>}
      <div ref={bottomRef} />
    </div>
  );
}
