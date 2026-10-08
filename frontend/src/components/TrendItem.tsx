import { TrendingUp, Eye, Clock } from 'lucide-react';
import { motion } from 'motion/react';
import { VerdictBadge } from './VerdictBadge';
import type { TrendingClaim } from '../services/api';

interface TrendItemProps {
  claim: TrendingClaim;
  onClick: () => void;
}

export function TrendItem({ claim, onClick }: TrendItemProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-xl p-4 cursor-pointer hover:shadow-lg transition-all"
    >
      <div className="flex items-start gap-3 mb-3">
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-orange-400 to-pink-500 rounded-lg flex items-center justify-center">
          <TrendingUp className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-gray-900 mb-2">{claim.claim}</p>
          <VerdictBadge verdict={claim.verdict} size="sm" />
        </div>
      </div>

      <div className="flex items-center gap-4 text-gray-500">
        <div className="flex items-center gap-1">
          <Eye className="w-4 h-4" />
          <span>{claim.views.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <Clock className="w-4 h-4" />
          <span>{formatTime(claim.timestamp)}</span>
        </div>
      </div>
    </motion.div>
  );
}
