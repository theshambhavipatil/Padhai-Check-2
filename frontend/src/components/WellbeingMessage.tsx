import { Heart } from 'lucide-react';
import { motion } from 'motion/react';

interface WellbeingMessageProps {
  message: string;
}

export function WellbeingMessage({ message }: WellbeingMessageProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gradient-to-r from-pink-50 to-purple-50 border border-pink-200 rounded-xl p-4"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full flex items-center justify-center">
          <Heart className="w-4 h-4 text-white" />
        </div>
        <div className="flex-1">
          <p className="text-purple-900">
            {message}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
