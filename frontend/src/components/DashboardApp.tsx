import { useState } from 'react';
import { Layout } from './Layout';
import { ChatPage } from '../pages/ChatPage';
import { TrendsPage } from '../pages/TrendsPage';
import { HistoryPage } from '../pages/HistoryPage';
import { ClaimDetailsPage } from '../pages/ClaimDetailsPage';

type Page = 'chat' | 'trends' | 'history' | 'claim-details';

interface DashboardAppProps {
  onBackToHome: () => void;
}

export function DashboardApp({ onBackToHome }: DashboardAppProps) {
  const [currentPage, setCurrentPage] = useState<Page>('chat');
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null);

  const handleNavigate = (page: Page, claimId?: string) => {
    setCurrentPage(page);
    if (claimId) {
      setSelectedClaimId(claimId);
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'chat':
        return <ChatPage />;
      case 'trends':
        return <TrendsPage onNavigate={handleNavigate} />;
      case 'history':
        return <HistoryPage onNavigate={handleNavigate} />;
      case 'claim-details':
        return <ClaimDetailsPage claimId={selectedClaimId} onNavigate={handleNavigate} />;
      default:
        return <ChatPage />;
    }
  };

  return (
    <Layout currentPage={currentPage} onNavigate={handleNavigate} onBackToHome={onBackToHome}>
      {renderPage()}
    </Layout>
  );
}
