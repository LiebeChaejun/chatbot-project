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

  if (messages.length === 0 && !loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-1 text-center px-4">
        <p className="text-gray-600 text-sm">새로운 대화를 시작해보세요.</p>
        <p className="text-gray-400 text-xs">
          이전 대화는 사이드바에서 확인할 수 있어요.
        </p>
      </div>
    );
  }

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
