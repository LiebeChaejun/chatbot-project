// src/components/ChatInput.tsx
import { useState, useRef, useEffect } from "react";

interface Props {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
  };

  useEffect(() => {
    if (!disabled) {
      inputRef.current?.focus();
    }
  }, [disabled]);

  return (
    <div className="flex gap-2 p-4 border-t">
      <input
        ref={inputRef}
        className="flex-1 border rounded-full px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-400"
        placeholder="메시지를 입력하세요..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        disabled={disabled}
      />
      <button
        onClick={handleSubmit}
        disabled={disabled}
        className="bg-blue-500 text-white px-4 py-2 rounded-full text-sm disabled:opacity-50"
      >
        전송
      </button>
    </div>
  );
}
