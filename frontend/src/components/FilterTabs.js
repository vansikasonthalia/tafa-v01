'use client';

export default function FilterTabs({ tabs, activeTab, onTabChange }) {
  return (
    <div className="filter-tabs">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          className={`filter-tab ${activeTab === tab.value ? 'active' : ''}`}
          onClick={() => onTabChange(tab.value)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
