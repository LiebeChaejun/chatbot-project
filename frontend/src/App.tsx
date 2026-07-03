// src/App.tsx
import { useChat } from "./hooks/useChat";
import { ChatHeader } from "./components/ChatHeader";
import { ChatWindow } from "./components/ChatWindow";
import { ChatInput } from "./components/ChatInput";
import { ErrorBanner } from "./components/ErrorBanner";

function App() {
  const { messages, sendMessage, loading, error } = useChat();

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto border-x">
      <ChatHeader />
      <ChatWindow messages={messages} loading={loading} />
      {error && <ErrorBanner message={error} />}
      <ChatInput onSend={sendMessage} disabled={loading} />
    </div>
  );
}

export default App;
