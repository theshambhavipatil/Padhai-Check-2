import { useState, useEffect, useRef } from 'react';
import { ChatBubble } from '../components/chat/ChatBubble';
import { ChatInput } from '../components/chat/ChatInput';
import { TypingIndicator } from '../components/chat/TypingIndicator';
import { AnimatePresence } from 'motion/react';
import { uploadFile, verifyContent, type VerificationResult } from '../services/api';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content?: string;
  files?: { name: string; url: string; type: string }[];
  verification?: VerificationResult;
  timestamp: Date;
}

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Hi! 👋 I\'m your AI study assistant. Ask me anything, upload screenshots or PDFs, and I\'ll help verify information and explain concepts!',
      timestamp: new Date(),
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (text: string, files: { name: string; url: string; type: string; file: File }[]) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: text,
      files: files.map(f => ({ name: f.name, url: f.url, type: f.type })),
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // Show typing indicator
    setIsTyping(true);

    try {
      // Upload files if any
      const fileIds: string[] = [];
      for (const file of files) {
        try {
          const result = await uploadFile(file.file);
          if ((result as any).file_id) fileIds.push((result as any).file_id);
        } catch (uploadError) {
          console.error('File upload failed:', uploadError);
          throw new Error(`Failed to upload file: ${uploadError instanceof Error ? uploadError.message : String(uploadError)}`);
        }
      }

      // Verify content
      const verification = await verifyContent({
        text: text || undefined,
        // verifyContent accepts file_urls which we map to backend file_ids
        file_urls: fileIds.length > 0 ? fileIds : undefined,
      });

      // Add AI response
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        verification,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);

      // NOTE: History is now automatically saved by backend when verifyContent() completes.
      // No need to call saveToHistory() anymore - backend /api/history endpoint tracks all verifications.
      console.log('Verification complete. History automatically saved server-side.');

    } catch (error) {
      console.error('Error verifying content:', error);
      
      // Add error message with details
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Error: ${error instanceof Error ? error.message : String(error)}\n\nPlease check:\n1. Is the backend running on http://localhost:5000?\n2. Is the GEMINI_API_KEY set?\n3. Check browser console (F12) for more details.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map(message => (
            <ChatBubble key={message.id} {...message} />
          ))}
          
          <AnimatePresence>
            {isTyping && <TypingIndicator />}
          </AnimatePresence>
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <ChatInput onSend={handleSend} disabled={isTyping} />
    </div>
  );
}
