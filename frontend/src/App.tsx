import { useState } from "react";
import { useChat } from "./hooks/useChat";
import { useConversations } from "./hooks/useConversations";
import { ChatHeader } from "./components/ChatHeader";
import { ChatWindow } from "./components/ChatWindow";
import { ChatInput } from "./components/ChatInput";
import { ErrorBanner } from "./components/ErrorBanner";
import { Sidebar } from "./components/Sidebar";

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);

  const {
    conversations,
    createConversation,
    touchConversation,
    refreshConversations,
  } = useConversations();

  const { messages, sendMessage, loading, error } = useChat(selectedThreadId);

  const currentTitle =
    conversations.find((c) => c.threadId === selectedThreadId)?.title ??
    "새 대화";

  const handleSend = async (content: string) => {
    let threadId = selectedThreadId;

    if (!threadId) {
      const conversation = await createConversation();
      threadId = conversation.threadId;
      setSelectedThreadId(threadId);
    }

    await sendMessage(content, threadId);
    touchConversation(threadId);

    // 첫 메시지였다면 백엔드가 제목을 자동 생성했을 테니, 목록을 다시 불러와 반영
    await refreshConversations();
  };

  const handleCreateNew = () => {
    setSelectedThreadId(null);
    setIsSidebarOpen(false);
  };

  return (
    <div className="flex h-screen">
      <Sidebar
        isOpen={isSidebarOpen}
        conversations={conversations}
        selectedThreadId={selectedThreadId}
        onSelect={(threadId) => {
          setSelectedThreadId(threadId);
          setIsSidebarOpen(false);
        }}
        onCreateNew={handleCreateNew}
      />

      <div className="flex flex-col flex-1 min-w-0">
        <ChatHeader
          title={currentTitle}
          onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        />
        <ChatWindow messages={messages} loading={loading} />
        {error && <ErrorBanner message={error} />}
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>
    </div>
  );
}

export default App;
