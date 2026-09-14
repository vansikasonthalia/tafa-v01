'use client';

import { useState, useEffect, useCallback } from 'react';
import FileDropZone from '@/components/FileDropZone';
import {
  uploadWatchlist,
  getWatchlist,
  removeTicker,
  clearWatchlist,
  runScreener,
  getScreenerStatus,
} from '@/lib/api';

export default function StocklistPage() {
  const [watchlist, setWatchlist] = useState([]);
  const [results, setResults] = useState(null);
  const [running, setRunning] = useState(false);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [error, setError] = useState(null);

  const loadWatchlist = useCallback(async () => {
    try {
      const data = await getWatchlist();
      setWatchlist(data.tickers || []);
    } catch (err) {
      console.error('Failed to load watchlist:', err);
    }
  }, []);

  const loadSchedulerStatus = useCallback(async () => {
    try {
      const data = await getScreenerStatus();
      setSchedulerStatus(data);
    } catch (err) {
      console.error('Failed to load scheduler status:', err);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadWatchlist();
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadSchedulerStatus();
    const interval = setInterval(loadSchedulerStatus, 30000);
    return () => clearInterval(interval);
  }, [loadWatchlist, loadSchedulerStatus]);

  const handleUpload = async (file) => {
    const result = await uploadWatchlist(file);
    await loadWatchlist();
    return result;
  };

  const handleRemoveTicker = async (ticker) => {
    try {
      await removeTicker(ticker);
      await loadWatchlist();
    } catch (err) {
      console.error('Failed to remove ticker:', err);
    }
  };

  const handleClearAll = async () => {
    try {
      await clearWatchlist();
      setWatchlist([]);
    } catch (err) {
      console.error('Failed to clear watchlist:', err);
    }
  };

  const handleRunScreener = async () => {
    setRunning(true);
    setError(null);
    setResults(null);

    try {
      const data = await runScreener();
      setResults(data);
    } catch (err) {
      setError(err.message || 'Screener failed to run.');
    } finally {
      setRunning(false);
      loadSchedulerStatus();
    }
  };

  const formatTime = (isoString) => {
    if (!isoString) return '—';
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      {/* Scheduler Status Bar */}
      <div className="scheduler-bar">
        <div className={`scheduler-dot ${schedulerStatus?.scheduler_active ? '' : 'inactive'}`}></div>
        <span className="scheduler-label">
          Auto-run:{' '}
          <strong>{schedulerStatus?.scheduler_active ? 'Every 30 min' : 'Inactive'}</strong>
          {schedulerStatus?.next_run && (
            <> · Next: <strong>{formatTime(schedulerStatus.next_run)}</strong></>
          )}
          {schedulerStatus?.last_run && (
            <> · Last: {formatTime(schedulerStatus.last_run)}</>
          )}
        </span>
      </div>

      {/* Page Header */}
      <div className="page-header">
        <h1>Stocklist</h1>
        <div className="header-actions">
          <h2>Stocklist</h2>
          <p>
            Upload your stock universe, configure rules, and run the screener to
            find buy/sell signals.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {watchlist.length > 0 && (
            <button className="btn btn-secondary" onClick={handleClearAll}>
              Clear all
            </button>
          )}
          <button
            className="btn btn-primary"
            onClick={handleRunScreener}
            disabled={running || watchlist.length === 0}
          >
            {running ? (
              <>
                <span className="spinner"></span>
                Running...
              </>
            ) : (
              'Run screener'
            )}
          </button>
        </div>
      </div>

      {/* File Upload */}
      <FileDropZone onUpload={handleUpload} disabled={running} />

      {/* Watchlist Table */}
      {watchlist.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden', marginTop: '24px' }}>
          <div className="card-header" style={{ padding: '16px 20px' }}>
            <span className="card-title">
              Watchlist — {watchlist.length} stock{watchlist.length !== 1 ? 's' : ''}
            </span>
          </div>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '60px' }}>#</th>
                  <th>Stock</th>
                  <th>Industry</th>
                  <th style={{ width: '60px' }}></th>
                </tr>
              </thead>
              <tbody>
                {watchlist.map((item, index) => (
                  <tr key={item.id}>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                      {index + 1}
                    </td>
                    <td>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <span className="ticker-cell">{item.ticker}</span>
                        {item.company_name && (
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                            {item.company_name}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      {item.industry ? (
                        <span className="badge badge-info">{item.industry}</span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)' }}>—</span>
                      )}
                    </td>
                    <td>
                      <button
                        onClick={() => handleRemoveTicker(item.ticker)}
                        title={`Remove ${item.ticker}`}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: 'var(--text-muted)',
                          cursor: 'pointer',
                          fontSize: '0.85rem',
                          padding: '4px 8px',
                          borderRadius: 'var(--radius-sm)',
                          transition: 'color 150ms',
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
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          marginTop: '24px',
          padding: '14px 20px',
          background: 'var(--red-muted)',
          border: '1px solid rgba(248,113,113,0.2)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--red)',
          fontSize: '0.82rem',
        }}>
          ❌ {error}
        </div>
      )}

      {/* Results */}
      <div style={{ marginTop: '24px' }}>
        {results ? (
          results.signals.length > 0 ? (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div className="card-header" style={{ padding: '16px 20px' }}>
                <span className="card-title">Signals Found</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Ticker</th>
                    <th>Signal</th>
                    <th>Price</th>
                    <th>RSI</th>
                    <th>EMA</th>
                    <th>EMA(RSI)</th>
                    <th>WMA(RSI)</th>
                  </tr>
                </thead>
                <tbody>
                  {results.signals.map((sig) => (
                    <tr key={sig.id}>
                      <td className="ticker-cell">{sig.ticker}</td>
                      <td>
                        <span className={`badge badge-${sig.signal.toLowerCase()}`}>
                          {sig.signal}
                        </span>
                      </td>
                      <td>{sig.price?.toFixed(2) || '—'}</td>
                      <td>{sig.rsi || '—'}</td>
                      <td>{sig.ema_value || '—'}</td>
                      <td>{sig.ema_rsi || '—'}</td>
                      <td>{sig.wma_rsi || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {results.errors?.length > 0 && (
                <div style={{ padding: '12px 16px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {results.errors.length} ticker(s) had errors and were skipped.
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <p>
                No signals found. Scanned {results.tickers_scanned} ticker{results.tickers_scanned !== 1 ? 's' : ''} —
                none matched all conditions.
                {results.errors?.length > 0 && ` (${results.errors.length} had errors)`}
              </p>
            </div>
          )
        ) : (
          !watchlist.length && (
            <div className="empty-state">
              <div className="empty-state-icon">🔍</div>
              <p>No results yet. Upload a watchlist and run the screener.</p>
            </div>
          )
        )}
      </div>
    </>
  );
}
