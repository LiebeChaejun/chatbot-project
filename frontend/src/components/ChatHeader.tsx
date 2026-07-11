import { useState, useRef, useEffect } from "react";

interface Props {
  title: string;
  onToggleSidebar: () => void;
  onRename: (newTitle: string) => void;
  canRename: boolean;
}

export function ChatHeader({
  title,
  onToggleSidebar,
  onRename,
  canRename,
}: Props) {
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(title);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setDraft(title);
  }, [title]);

  useEffect(() => {
    if (isEditing) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [isEditing]);

  const startEditing = () => {
    if (!canRename) return;
    setDraft(title);
    setIsEditing(true);
  };

  const commitEdit = () => {
    const trimmed = draft.trim();
    if (trimmed && trimmed !== title) {
      onRename(trimmed);
    }
    setIsEditing(false);
  };

  const cancelEdit = () => {
    setDraft(title);
    setIsEditing(false);
  };

  return (
    <header className="flex items-center gap-3 p-4 border-b">
      <button
        onClick={onToggleSidebar}
        className="text-gray-500 hover:text-gray-700"
        aria-label="사이드바 토글"
      >
        ☰
      </button>

      {isEditing ? (
        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={commitEdit}
          onKeyDown={(e) => {
            if (e.key === "Enter") commitEdit();
            if (e.key === "Escape") cancelEdit();
          }}
          className="text-sm font-medium flex-1 min-w-0 border-b border-blue-400 outline-none"
        />
      ) : (
        <p className="text-sm font-medium flex-1 truncate">{title}</p>
      )}

      {canRename && !isEditing && (
        <button
          onClick={startEditing}
          className="text-gray-400 hover:text-gray-600 text-sm"
          aria-label="제목 수정"
        >
          ✏️
        </button>
      )}
    </header>
  );
}
