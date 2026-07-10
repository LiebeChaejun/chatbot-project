import type { Conversation } from "../types/conversation";
import { Button } from "./Button";

interface Props {
  isOpen: boolean;
  conversations: Conversation[];
  selectedThreadId: string | null;
  onSelect: (threadId: string) => void;
  onCreateNew: () => void;
}

export function Sidebar({
  isOpen,
  conversations,
  selectedThreadId,
  onSelect,
  onCreateNew,
}: Props) {
  return (
    <div
      className="overflow-hidden border-r transition-[width] duration-200 flex-shrink-0"
      style={{ width: isOpen ? "220px" : "0px" }}
    >
      <div className="w-[220px] h-full flex flex-col">
        <div className="p-3">
          <Button variant="secondary" onClick={onCreateNew} className="w-full">
            + 새 대화
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto px-2">
          {conversations.map((conv) => (
            <div
              key={conv.threadId}
              onClick={() => onSelect(conv.threadId)}
              className={`px-3 py-2 rounded-lg mb-1 cursor-pointer truncate text-sm ${
                conv.threadId === selectedThreadId
                  ? "bg-blue-50 text-blue-600 font-medium"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              {conv.title}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
