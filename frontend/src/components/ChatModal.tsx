import { useState, useEffect, useRef } from 'react';
import { X, Minimize2, Maximize2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ChatBubble } from './chat/ChatBubble';
import { ChatInput } from './chat/ChatInput';
import { TypingIndicator } from './chat/TypingIndicator';
import { uploadFile, verifyContent, saveToHistory, type VerificationResult } from '../services/api';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content?: string;
  files?: { name: string; url: string; type: string }[];
  verification?: VerificationResult;
  timestamp: Date;
}

interface ChatModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChatModal({ isOpen, onClose }: ChatModalProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Hi! 👋 I\'m your AI study assistant. Ask me anything, upload screenshots or PDFs, and I\'ll help verify information and explain concepts!',
      timestamp: new Date(),
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen && !isMinimized) {
      scrollToBottom();
    }
  }, [messages, isTyping, isOpen, isMinimized]);

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
        // verifyContent accepts file_urls which will be mapped to backend file_ids
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

      // Save to history
      saveToHistory({
        id: Date.now().toString(),
        query: text || `Uploaded ${files.length} file(s)`,
        verdict: verification.verdict,
        timestamp: new Date().toISOString(),
        hasImage: files.length > 0,
      });
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
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop for mobile */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/20 z-40 lg:hidden"
          />

          {/* Chat Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ 
              opacity: 1, 
              scale: 1, 
              y: 0,
              height: isMinimized ? '64px' : 'auto'
            }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-6 right-6 z-50 w-full max-w-md lg:max-w-lg bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden flex flex-col"
            style={{ 
              maxHeight: isMinimized ? '64px' : 'calc(100vh - 120px)',
              margin: '0 1rem 1.5rem'
            }}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 flex items-center justify-between flex-shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <span>🤖</span>
                </div>
                <div>
                  <h3 className="text-white">AI Study Assistant</h3>
                  {!isMinimized && <p className="text-white/80 text-sm">Online</p>}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  title={isMinimized ? 'Maximize' : 'Minimize'}
                >
                  {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
                </button>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  title="Close"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Chat Content */}
            {!isMinimized && (
              <>
                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 bg-gray-50">
                  {messages.map(message => (
                    <ChatBubble key={message.id} {...message} />
                  ))}
                  
                  <AnimatePresence>
                    {isTyping && <TypingIndicator />}
                  </AnimatePresence>
                  
                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="flex-shrink-0 bg-white">
                  <ChatInput onSend={handleSend} disabled={isTyping} />
                </div>
              </>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
