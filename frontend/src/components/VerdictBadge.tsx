import { CheckCircle, XCircle, AlertTriangle, HelpCircle } from 'lucide-react';
import { motion } from 'motion/react';

interface VerdictBadgeProps {
  verdict: 'True' | 'False' | 'Misleading' | 'Unverified';
  size?: 'sm' | 'md' | 'lg';
}

export function VerdictBadge({ verdict, size = 'md' }: VerdictBadgeProps) {
  const config = {
    True: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-700',
      icon: CheckCircle,
    },
    False: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-700',
      icon: XCircle,
    },
    Misleading: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-700',
      icon: AlertTriangle,
    },
    Unverified: {
      bg: 'bg-gray-50',
      border: 'border-gray-200',
      text: 'text-gray-700',
      icon: HelpCircle,
    },
  };

  const sizeConfig = {
    sm: { padding: 'px-2 py-1', iconSize: 'w-3 h-3' },
    md: { padding: 'px-3 py-2', iconSize: 'w-4 h-4' },
    lg: { padding: 'px-4 py-3', iconSize: 'w-5 h-5' },
  };

  const { bg, border, text, icon: Icon } = config[verdict];
  const { padding, iconSize } = sizeConfig[size];

  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={`inline-flex items-center gap-2 ${bg} ${border} ${text} border rounded-lg ${padding}`}
    >
      <Icon className={iconSize} />
      <span>{verdict}</span>
    </motion.div>
  );
}
