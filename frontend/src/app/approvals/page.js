'use client';

import { useState } from 'react';
import FilterTabs from '@/components/FilterTabs';

const TABS = [
  { label: 'Pending', value: 'pending' },
  { label: 'Placed', value: 'placed' },
  { label: 'Rejected', value: 'rejected' },
  { label: 'All', value: 'all' },
];

export default function ApprovalsPage() {
  const [activeTab, setActiveTab] = useState('pending');

  return (
    <>
      <div className="page-header">
        <div className="page-header-text">
          <h2>Approvals</h2>
          <p>
            Every signal lands here first. Nothing reaches Zerodha until you
            approve it.
          </p>
        </div>
        <FilterTabs tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      <div className="placeholder-banner">
        <span className="placeholder-banner-icon">🔧</span>
        <span>
          This feature is coming soon. Once Zerodha integration is active,
          pending signals will appear here for your review before any orders are placed.
        </span>
      </div>

      <div className="empty-state">
        <div className="empty-state-icon">✅</div>
        <p>
          Nothing waiting on you. When you connect Zerodha and run the screener,
          signals will appear here for approval before orders are placed.
        </p>
      </div>
    </>
  );
}
