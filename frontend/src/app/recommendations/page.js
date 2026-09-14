'use client';

import { useState, useEffect, useCallback } from 'react';
import FilterTabs from '@/components/FilterTabs';
import { getTrackingEntries, deleteTrackingEntry } from '@/lib/api';

const TABS = [
  { label: 'All', value: 'all' },
  { label: 'Buy', value: 'BUY' },
  { label: 'Sell', value: 'SELL' },
];

export default function RecommendationsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadEntries = useCallback(async () => {
    setLoading(true);
    try {
      const signal = activeTab === 'all' ? null : activeTab;
      const data = await getTrackingEntries(signal);
      setEntries(data.entries || []);
    } catch (err) {
      console.error('Failed to load entries:', err);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadEntries();
  }, [loadEntries]);

  const handleDelete = async (id) => {
    try {
      await deleteTrackingEntry(id);
      setEntries((prev) => prev.filter((e) => e.id !== id));
    } catch (err) {
      console.error('Failed to delete entry:', err);
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return '—';
    const d = new Date(isoString);
    return d.toLocaleDateString([], {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    }) + ' ' + d.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <>
      <div className="page-header">
        <div className="page-header-text">
          <h2>Recommendations</h2>
          <p>
            Every buy/sell recommendation the screener generates, stamped with
            indicator values at signal time.
          </p>
        </div>
        <FilterTabs tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {loading ? (
        <div className="empty-state">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
        </div>
      ) : entries.length > 0 ? (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Signal</th>
                <th>Price</th>
                <th>Mkt Cap (Cr)</th>
                <th>RSI</th>
                <th>EMA(RSI)</th>
                <th>WMA(RSI)</th>
                <th>Source</th>
                <th>Time</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.id}>
                  <td className="ticker-cell">{entry.ticker}</td>
                  <td>
                    <span className={`badge badge-${entry.signal.toLowerCase()}`}>
                      {entry.signal}
                    </span>
                  </td>
                  <td>{entry.price?.toFixed(2) || '—'}</td>
                  <td>{entry.market_cap ? `${entry.market_cap.toLocaleString()}` : '—'}</td>
                  <td>{entry.rsi || '—'}</td>
                  <td>{entry.ema_rsi || '—'}</td>
                  <td>{entry.wma_rsi || '—'}</td>
                  <td>
                    <span className={`badge ${entry.run_type === 'scheduled' ? 'badge-info' : 'badge-pending'}`}>
                      {entry.run_type}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    {formatDate(entry.timestamp)}
                  </td>
                  <td>
                    <button
                      className="btn-ghost"
                      onClick={() => handleDelete(entry.id)}
                      title="Delete entry"
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        padding: '4px 8px',
                        borderRadius: 'var(--radius-sm)',
                      }}
                      onMouseEnter={(e) => e.target.style.color = 'var(--red)'}
                      onMouseLeave={(e) => e.target.style.color = 'var(--text-muted)'}
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">📝</div>
          <p>
            No recommendations yet. They appear here automatically when
            the screener fires a buy or sell signal.
          </p>
        </div>
      )}
    </>
  );
}
