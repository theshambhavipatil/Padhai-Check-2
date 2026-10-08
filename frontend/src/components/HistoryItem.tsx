import { Clock, Image, MessageSquare } from 'lucide-react';
import { motion } from 'motion/react';
import { VerdictBadge } from './VerdictBadge';
import type { HistoryItem as HistoryItemType } from '../services/api';

interface HistoryItemProps {
  item: HistoryItemType;
  onClick: () => void;
}

export function HistoryItem({ item, onClick }: HistoryItemProps) {
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 48) return 'Yesterday';
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-xl p-4 cursor-pointer hover:shadow-lg transition-all"
    >
      <div className="flex items-start gap-3">
        <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${
          item.hasImage 
            ? 'bg-gradient-to-br from-blue-400 to-purple-500'
            : 'bg-gradient-to-br from-green-400 to-teal-500'
        }`}>
          {item.hasImage ? (
            <Image className="w-5 h-5 text-white" />
          ) : (
            <MessageSquare className="w-5 h-5 text-white" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-gray-900 mb-2 line-clamp-2">{item.query}</p>
          <div className="flex items-center gap-3 flex-wrap">
            <VerdictBadge verdict={item.verdict} size="sm" />
            <div className="flex items-center gap-1 text-gray-500">
              <Clock className="w-4 h-4" />
              <span>{formatDate(item.timestamp)}</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
