'use client';

import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/components/ui/use-toast';
import { Loader2 } from 'lucide-react';
import axios, { AxiosError } from 'axios';
import React, { useEffect, useRef, useState } from 'react';
import { useSession } from 'next-auth/react';
import { User } from 'next-auth';

interface ChatMessage {
  user: string;
  bot: string;
  timestamp?: string;
}

function ChatbotDashboard() {
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const { toast } = useToast();
  const { data: session } = useSession();
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!message.trim() || isLoading) return;
    setIsLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        message: message.trim(),
        session_id: sessionId || null,
      });

      const newSessionId = response.data.session_id;
      setSessionId(newSessionId);

      setChatHistory((prev) => [
        ...prev,
        {
          user: message.trim(),
          bot: response.data.bot_response,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
      setMessage('');
    } catch (error) {
      const axiosError = error as AxiosError;
      toast({
        title: 'Error',
        description:
          (axiosError.response?.data && typeof axiosError.response.data === 'object' && 'message' in axiosError.response.data
            ? (axiosError.response.data as { message?: string }).message
            : undefined) ?? 'Failed to chat',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    const container = chatContainerRef.current;
    if (container) container.scrollTop = container.scrollHeight;
  }, [chatHistory]);

  if (!session?.user) return null;

  return (
    <div className="my-8 mx-4 md:mx-8 lg:mx-auto p-6 bg-white rounded w-full max-w-4xl">
      <h1 className="text-4xl font-bold mb-4">Chatbot Dashboard</h1>
      <Separator className="mb-4" />

      <div
        ref={chatContainerRef}
        className="mb-4 space-y-4 max-h-[400px] overflow-y-auto border rounded p-4 bg-gray-50"
      >
        {chatHistory.length === 0 ? (
          <p className="text-center text-gray-400">Start chatting with the bot...</p>
        ) : (
          chatHistory.map((chat, index) => (
            <div key={index} className="space-y-1">
              <div className="bg-blue-100 p-2 rounded text-sm max-w-fit">
                <span className="font-semibold">You:</span> {chat.user}
              </div>
              <div className="bg-green-100 p-2 rounded text-sm max-w-fit">
                <span className="font-semibold">Bot:</span> {chat.bot}
              </div>
              <div className="text-xs text-gray-500">{chat.timestamp}</div>
            </div>
          ))
        )}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={message}
          placeholder="Type your message..."
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyPress}
          className="flex-1 p-2 border rounded"
          disabled={isLoading}
        />
        <Button onClick={sendMessage} disabled={isLoading}>
          {isLoading ? <Loader2 className="animate-spin w-4 h-4" /> : 'Send'}
        </Button>
      </div>
    </div>
  );
}

export default ChatbotDashboard;
