import React, { useState, useRef, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MessageBubble from './components/MessageBubble';
import TracePanel from './components/TracePanel';
import InputBar from './components/InputBar';
import { Message, TraceStep, WindowMemoryItem } from './types';
import { sendMessage, ChatResponse } from './services/api';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Welcome to the XYZ University advisory portal. How can I help you today?",
      timestamp: new Date(),
    }
  ]);
  const [windowMemory, setWindowMemory] = useState<WindowMemoryItem[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [traceOpen, setTraceOpen] = useState(false);
  const [activeTrace, setActiveTrace] = useState<{ steps: TraceStep[], path: string }>({ steps: [], path: "" });

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const updateWindowMemory = (userMsg: string, botMsg: string) => {
    setWindowMemory(prev => {
      const newItems: WindowMemoryItem[] = [
        { role: 'user', content: userMsg },
        { role: 'assistant', content: botMsg }
      ];
      const combined = [...prev, ...newItems];
      return combined.slice(-4);
    });
  };

  const handleSend = async (forcedQuery?: string) => {
    const query = forcedQuery || inputText;
    if (!query.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    const botPlaceholderId = (Date.now() + 1).toString();
    const botLoadingMessage: Message = {
      id: botPlaceholderId,
      role: 'assistant',
      content: "",
      timestamp: new Date(),
      isLoading: true
    };
    setMessages(prev => [...prev, botLoadingMessage]);

    try {
      const response: ChatResponse = await sendMessage({
        query,
        window_memory: windowMemory
      });

      const traceSteps: TraceStep[] = response.trace.map((t, i) => ({
        ...t,
        id: `t-${Date.now()}-${i}`,
        timestamp: new Date()
      }));

      const botMessage: Message = {
        id: botPlaceholderId,
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        trace: traceSteps,
        path: response.path
      };

      setMessages(prev => prev.map(m => m.id === botPlaceholderId ? botMessage : m));
      setActiveTrace({ steps: traceSteps, path: response.path });
      updateWindowMemory(query, response.answer);
      
    } catch (error) {
      const errorMessage: Message = {
        id: botPlaceholderId,
        role: 'assistant',
        content: "System error: Failed to connect to university records.",
        timestamp: new Date(),
      };
      setMessages(prev => prev.map(m => m.id === botPlaceholderId ? errorMessage : m));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#070B14] text-slate-200 overflow-hidden font-body">
      <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar 
          isOpen={sidebarOpen} 
          onQuickTopic={handleSend} 
          windowMemory={windowMemory} 
        />

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col relative overflow-hidden">
          {/* Messages Feed */}
          <div 
            ref={scrollRef}
            className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth"
          >
            <div className="max-w-4xl mx-auto w-full">
              {messages.map((msg) => (
                <MessageBubble 
                  key={msg.id} 
                  message={msg} 
                  onTraceClick={() => setTraceOpen(true)}
                />
              ))}
            </div>
          </div>

          {/* Trace Panel */}
          <TracePanel 
            isOpen={traceOpen} 
            onToggle={() => setTraceOpen(!traceOpen)} 
            steps={activeTrace.steps}
            path={activeTrace.path}
          />

          {/* Input Area */}
          <div className="w-full">
             <InputBar 
              value={inputText} 
              onChange={setInputText} 
              onSend={() => handleSend()} 
              isLoading={isLoading} 
            />
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
