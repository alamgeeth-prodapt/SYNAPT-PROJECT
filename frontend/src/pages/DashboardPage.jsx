import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Activity } from 'lucide-react';

import DisruptionsTable from '../components/DisruptionsTable';
import DisruptionAnalytics from '../components/DisruptionAnalytics';
import CrisisResponseCenter from '../components/CrisisResponseCenter';
import SQLConsole from '../components/SQLConsole';
import ExecutiveCopilot from '../components/ExecutiveCopilot';
import { prefetchAnalyticsOverview } from '../api/analytics';

export default function DashboardPage() {
  const { user, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('table'); // 'table' | 'crisis' | 'sql' | 'copilot'
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/login');
    }
  }, [loading, isAuthenticated, navigate]);

  useEffect(() => {
    if (isAuthenticated) {
      prefetchAnalyticsOverview();
      fetch('/health')
        .then((res) => res.json())
        .then((data) => setHealth(data))
        .catch((err) => console.error('Health check failed:', err));
    }
  }, [isAuthenticated]);

  if (loading || !isAuthenticated) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-neutral-500 text-sm">
        <Activity className="w-4 h-4 animate-spin mr-2.5" />
        <span>Verifying your session…</span>
      </div>
    );
  }

  // When user clicks "Analyze" on any historical record in the table:
  const handleAnalyzeFromTable = (incident) => {
    setSelectedIncident(incident);
    setActiveTab('crisis');
    window.scrollTo({ top: 120, behavior: 'smooth' });
  };

  const dashboardTabs = [
    { id: 'analytics', name: 'Disruption analytics' },
    { id: 'table', name: 'Disruption history' },
    { id: 'crisis', name: 'Crisis response' },
    { id: 'sql', name: 'SQL assistant' },
    { id: 'copilot', name: 'Executive AI Copilot' },
  ];

  return (
    <div className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full">
      <header className="mb-8">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>Enterprise Crisis Command Active</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-950">
          Supply Chain Crisis Operations
        </h1>
        <p className="mt-1.5 text-xs sm:text-sm text-slate-600 font-medium">
          Operator: <strong className="text-slate-900">{user?.username}</strong> ({user?.role || 'admin'}) ·{' '}
          <strong className="text-slate-900 font-mono">{(health?.total_records || 100000).toLocaleString()}</strong> historical records ·{' '}
          <strong className="text-slate-900 font-mono">3</strong> XGBoost models loaded
        </p>
      </header>

      <div role="tablist" className="flex flex-wrap items-center gap-x-8 border-b border-slate-200/90 mb-8">
        {dashboardTabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3.5 -mb-px text-sm border-b-2 transition-all ${
                isActive
                  ? 'border-slate-950 text-slate-950 font-bold'
                  : 'border-transparent text-slate-500 hover:text-slate-900 font-medium'
              }`}
            >
              {tab.name}
            </button>
          );
        })}
      </div>

      {activeTab === 'analytics' && <DisruptionAnalytics />}
      {activeTab === 'table' && <DisruptionsTable onSelectIncident={handleAnalyzeFromTable} />}
      {activeTab === 'crisis' && <CrisisResponseCenter prefilledIncident={selectedIncident} />}
      {activeTab === 'sql' && <SQLConsole />}
      {activeTab === 'copilot' && <ExecutiveCopilot />}
    </div>
  );
}
