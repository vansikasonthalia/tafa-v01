'use client';

import { useState, useEffect } from 'react';
import { getConfig, updateConfig } from '@/lib/api';

const TIMEFRAME_OPTIONS = [
  { label: 'Day', value: '1d' },
  { label: 'Week', value: '1wk' },
  { label: 'Month', value: '1mo' },
];

export default function RulesPage() {
  const [config, setConfig] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await getConfig();
        setConfig(data);
      } catch (err) {
        console.error('Failed to load config:', err);
      }
    })();
  }, []);

  const handleChange = async (key, value) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);

    setSaving(true);
    setSaved(false);
    try {
      await updateConfig({ [key]: value });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error('Failed to save config:', err);
    } finally {
      setSaving(false);
    }
  };

  if (!config) {
    return (
      <div className="empty-state">
        <div className="spinner" style={{ margin: '0 auto' }}></div>
      </div>
    );
  }

  return (
    <>
      <div className="page-header">
        <div className="page-header-text">
          <h2>Rules</h2>
          <p>
            These parameters drive the buy criteria exactly; the sell criteria
            mirror them automatically (RSI below threshold, price crosses below
            the EMA, EMA(RSI) below WMA(RSI)).
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {saving && <span className="spinner"></span>}
          {saved && (
            <span style={{ fontSize: '0.78rem', color: 'var(--green)' }}>✓ Saved</span>
          )}
        </div>
      </div>

      {/* Indicator Parameters */}
      <div className="card" style={{ padding: 0 }}>
        <div className="form-group">
          <div className="form-label-wrap">
            <div className="form-label">Price EMA period</div>
            <div className="form-hint">Crossover reference line (default 11)</div>
          </div>
          <input
            type="number"
            className="form-input"
            value={config.price_ema_period || ''}
            onChange={(e) => handleChange('price_ema_period', e.target.value)}
            min="1"
          />
        </div>

        <div className="form-group">
          <div className="form-label-wrap">
            <div className="form-label">RSI period</div>
            <div className="form-hint">Standard lookback (default 14)</div>
          </div>
          <input
            type="number"
            className="form-input"
            value={config.rsi_period || ''}
            onChange={(e) => handleChange('rsi_period', e.target.value)}
            min="1"
          />
        </div>

        <div className="form-group">
          <div className="form-label-wrap">
            <div className="form-label">EMA of RSI period</div>
            <div className="form-hint">Fast RSI-momentum line (default 3)</div>
          </div>
          <input
            type="number"
            className="form-input"
            value={config.ema_of_rsi_period || ''}
            onChange={(e) => handleChange('ema_of_rsi_period', e.target.value)}
            min="1"
          />
        </div>

        <div className="form-group">
          <div className="form-label-wrap">
            <div className="form-label">WMA of RSI period</div>
            <div className="form-hint">Slow RSI-momentum line (default 21)</div>
          </div>
          <input
            type="number"
            className="form-input"
            value={config.wma_of_rsi_period || ''}
            onChange={(e) => handleChange('wma_of_rsi_period', e.target.value)}
            min="1"
          />
        </div>

        <div className="form-group">
          <div className="form-label-wrap">
            <div className="form-label">RSI threshold</div>
            <div className="form-hint">Buy above / sell below (default 50)</div>
          </div>
          <input
            type="number"
            className="form-input"
            value={config.rsi_threshold || ''}
            onChange={(e) => handleChange('rsi_threshold', e.target.value)}
            min="0"
            max="100"
          />
        </div>

        <div className="form-group">
          <div className="form-label-wrap">
            <div className="form-label">Timeframe</div>
            <div className="form-hint">Bar interval used for every calculation above</div>
          </div>
          <select
            className="form-select"
            value={config.timeframe || '1wk'}
            onChange={(e) => handleChange('timeframe', e.target.value)}
          >
            {TIMEFRAME_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Data Source */}
      <div className="section-label">Price data source</div>
      <div className="card" style={{ padding: 0 }}>
        <div className="form-group">
          <div className="form-label-wrap">
            <div className="form-label">Where candles come from</div>
            <div className="form-hint">
              Kite needs an active connection — see the Zerodha tab
            </div>
          </div>
          <select
            className="form-select"
            value={config.data_source || 'yahoo'}
            onChange={(e) => handleChange('data_source', e.target.value)}
          >
            <option value="yahoo">Yahoo Finance (free)</option>
            <option value="kite" disabled>Kite Connect (coming soon)</option>
          </select>
        </div>
      </div>

      {/* Scheduler Info */}
      <div className="section-label">Auto-run schedule</div>
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="badge badge-success">Active</span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            The screener runs automatically every <strong style={{ color: 'var(--text-primary)' }}>30 minutes</strong> while the backend is running.
          </span>
        </div>
      </div>
    </>
  );
}
