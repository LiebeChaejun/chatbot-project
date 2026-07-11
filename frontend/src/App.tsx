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
    renameConversation,
  } = useConversations();

  const { messages, sendMessage, loading, error } = useChat(selectedThreadId);

  const currentTitle =
    conversations.find((c) => c.threadId === selectedThreadId)?.title ??
    "새 대화";

  const handleSend = async (content: string) => {
    let threadId = selectedThreadId;
    const isNewConversation = !threadId;

    if (!threadId) {
      const conversation = await createConversation();
      threadId = conversation.threadId;
      setSelectedThreadId(threadId);
    }

    await sendMessage(content, threadId);
    touchConversation(threadId);

    if (isNewConversation) {
      await refreshConversations();
    } else {
      touchConversation(threadId);
    }
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
          onRename={(newTitle) => {
            if (selectedThreadId) {
              renameConversation(selectedThreadId, newTitle);
            }
          }}
          canRename={!!selectedThreadId}
        />
        <ChatWindow messages={messages} loading={loading} />
        {error && <ErrorBanner message={error} />}
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>
    </div>
  );
}

export default App;
