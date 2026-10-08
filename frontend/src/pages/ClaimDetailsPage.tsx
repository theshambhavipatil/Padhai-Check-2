import { useState, useEffect } from 'react';
import { ArrowLeft, Loader2, Clock } from 'lucide-react';
import { VerdictBadge } from '../components/VerdictBadge';
import { EvidenceCard } from '../components/EvidenceCard';
import { WellbeingMessage } from '../components/WellbeingMessage';
import { getClaimDetails, type ClaimDetails } from '../services/api';

interface ClaimDetailsPageProps {
  claimId: string | null;
  onNavigate: (page: 'chat' | 'trends' | 'history') => void;
}

export function ClaimDetailsPage({ claimId, onNavigate }: ClaimDetailsPageProps) {
  const [claim, setClaim] = useState<ClaimDetails | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (claimId) {
      loadClaimDetails();
    }
  }, [claimId]);

  const loadClaimDetails = async () => {
    if (!claimId) return;

    try {
      setLoading(true);
      const data = await getClaimDetails(claimId);
      setClaim(data);
    } catch (error) {
      console.error('Error loading claim details:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (!claim) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <h3 className="text-gray-900 mb-2">Claim not found</h3>
          <p className="text-gray-600 mb-4">The claim you're looking for doesn't exist.</p>
          <button
            onClick={() => onNavigate('chat')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Chat
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Back Button */}
        <button
          onClick={() => onNavigate('trends')}
          className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Trends</span>
        </button>

        {/* Claim Header */}
        <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-6">
          <div className="flex items-center gap-2 text-gray-500 mb-3">
            <Clock className="w-4 h-4" />
            <span>{formatDate(claim.timestamp)}</span>
          </div>
          
          <h1 className="text-gray-900 mb-4">{claim.claim}</h1>
          
          <VerdictBadge verdict={claim.verdict} size="lg" />
        </div>

        {/* Explanation */}
        <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-6">
          <h2 className="text-gray-900 mb-3">Detailed Explanation</h2>
          <p className="text-gray-700 leading-relaxed">{claim.explanation}</p>
        </div>

        {/* Evidence */}
        {claim.evidence.length > 0 && (
          <div className="mb-6">
            <h2 className="text-gray-900 mb-4">Evidence from Trusted Sources</h2>
            <div className="space-y-3">
              {claim.evidence.map((evidence, idx) => (
                <EvidenceCard key={idx} evidence={evidence} />
              ))}
            </div>
          </div>
        )}

        {/* Wellbeing Message */}
        {claim.wellbeing_message && (
          <WellbeingMessage message={claim.wellbeing_message} />
        )}

        {/* Action Buttons */}
        <div className="mt-8 flex gap-3">
          <button
            onClick={() => onNavigate('chat')}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Ask a Question
          </button>
          <button
            onClick={() => onNavigate('trends')}
            className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            View More Trends
          </button>
        </div>
      </div>
    </div>
  );
}
