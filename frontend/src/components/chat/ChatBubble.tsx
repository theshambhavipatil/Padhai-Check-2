import { motion } from 'motion/react';
import { Bot, User } from 'lucide-react';
import { VerdictBadge } from '../VerdictBadge';
import { EvidenceCard } from '../EvidenceCard';
import { WellbeingMessage } from '../WellbeingMessage';
import type { VerificationResult } from '../../services/api';
import { renderFormattedText } from '../../utils/textFormatter';

interface ChatBubbleProps {
  type: 'user' | 'ai';
  content?: string;
  files?: { name: string; url: string; type: string }[];
  verification?: VerificationResult;
  timestamp: Date;
}

export function ChatBubble({ type, content, files, verification, timestamp }: ChatBubbleProps) {
  const isUser = type === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-gradient-to-br from-green-400 to-blue-500' 
          : 'bg-gradient-to-br from-purple-400 to-pink-500'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 max-w-2xl ${isUser ? 'flex flex-col items-end' : ''}`}>
        {/* Text Message */}
        {content && (
          <div className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}>
            <p className="whitespace-pre-wrap">{content}</p>
          </div>
        )}

        {/* File Previews */}
        {files && files.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {files.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-3 py-2 max-w-xs"
              >
                {file.type.startsWith('image/') ? (
                  <img src={file.url} alt={file.name} className="w-12 h-12 rounded object-cover" />
                ) : (
                  <div className="w-12 h-12 bg-red-100 rounded flex items-center justify-center">
                    <span>📄</span>
                  </div>
                )}
                <span className="truncate flex-1">{file.name}</span>
              </div>
            ))}
          </div>
        )}

        {/* Verification Results */}
        {verification && (
          <div className="mt-3 space-y-3 w-full">
            {/* Verdict Badge */}
            <VerdictBadge verdict={verification.verdict} />

            {/* Explanation */}
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <div className="text-gray-700 leading-relaxed">
                {renderFormattedText(verification.explanation)}
              </div>
            </div>

            {/* Evidence Cards */}
            {verification.evidence.length > 0 && (
              <div className="space-y-2">
                <p className="text-gray-600">Evidence from trusted sources:</p>
                <div className="space-y-2">
                  {verification.evidence.map((evidence, idx) => (
                    <EvidenceCard key={idx} evidence={evidence} index={idx} />
                  ))}
                </div>
              </div>
            )}

            {/* Wellbeing Message */}
            {verification.wellbeing_message && (
              <WellbeingMessage message={verification.wellbeing_message} />
            )}
          </div>
        )}

        {/* Timestamp */}
        <p className={`text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {timestamp.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
        </p>
      </div>
    </motion.div>
  );
}
