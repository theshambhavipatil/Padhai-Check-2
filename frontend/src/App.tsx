import { useState } from 'react';
import { LandingPage } from './pages/LandingPage';
import { DashboardApp } from './components/DashboardApp';

export default function App() {
  const [showDashboard, setShowDashboard] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      {showDashboard ? (
        <DashboardApp onBackToHome={() => setShowDashboard(false)} />
      ) : (
        <LandingPage onOpenDashboard={() => setShowDashboard(true)} />
      )}
    </div>
  );
}