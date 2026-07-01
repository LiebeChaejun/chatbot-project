// src/App.tsx
import { useChat } from "./hooks/useChat";
import { ChatWindow } from "./components/ChatWindow";
import { ChatInput } from "./components/ChatInput";

function App() {
  const { messages, sendMessage, loading, error } = useChat();

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto border-x">
      <header className="p-4 border-b font-semibold">교육 플랫폼 챗봇</header>
      <ChatWindow messages={messages} loading={loading} />
      {error && (
        <div className="px-4 py-2 text-red-500 text-sm bg-red-50">{error}</div>
      )}
      <ChatInput onSend={sendMessage} disabled={loading} />
    </div>
  );
}

export default App;
