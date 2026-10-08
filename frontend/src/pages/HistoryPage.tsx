import { useState, useEffect } from 'react';
import { History, Loader2 } from 'lucide-react';
import { HistoryItem } from '../components/HistoryItem';
import { getHistory, type HistoryItem as HistoryItemType } from '../services/api';

interface HistoryPageProps {
  onNavigate: (page: 'claim-details', claimId: string) => void;
}

export function HistoryPage({ onNavigate }: HistoryPageProps) {
  const [history, setHistory] = useState<HistoryItemType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Loading history...');

      const data = await getHistory();
      console.log('History loaded:', data);

      setHistory(data);
    } catch (error) {
      console.error('Error loading history:', error);
      setError(error instanceof Error ? error.message : 'Failed to load history');
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-xl flex items-center justify-center">
              <History className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-gray-900">Verification History</h1>
              <p className="text-gray-600">Your past fact-checks and verifications</p>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            <p className="ml-3 text-gray-600">Loading history...</p>
          </div>
        )}

        {/* Error State */}
        {!loading && error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
            <button
              onClick={loadHistory}
              className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        )}

        {/* History List */}
        {!loading && !error && history.length > 0 && (
          <div className="space-y-4">
            {history.map((item) => (
              <HistoryItem
                key={item.id}
                item={item}
                onClick={() => onNavigate('claim-details', item.id)}
              />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && history.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <History className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-gray-900 mb-2">No history yet</h3>
            <p className="text-gray-600">Start chatting to build your verification history!</p>
          </div>
        )}
      </div>
    </div>
  );
}
