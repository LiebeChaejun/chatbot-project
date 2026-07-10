interface Props {
  title: string;
  onToggleSidebar: () => void;
}

export function ChatHeader({ title, onToggleSidebar }: Props) {
  return (
    <header className="flex items-center gap-3 p-4 border-b">
      <button
        onClick={onToggleSidebar}
        className="text-gray-500 hover:text-gray-700"
        aria-label="사이드바 토글"
      >
        ☰
      </button>
      <p className="text-sm font-medium flex-1 truncate">{title}</p>
    </header>
  );
}
