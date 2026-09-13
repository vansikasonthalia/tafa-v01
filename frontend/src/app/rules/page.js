'use client';

import { useState, useEffect } from 'react';
import FilterTabs from '@/components/FilterTabs';
import { getConfig, updateConfig } from '@/lib/api';

const RULE_TABS = [
  { label: 'Technical Analysis', value: 'technical' },
  { label: 'Fundamental Analysis', value: 'fundamental' },
];

const TIMEFRAME_OPTIONS = [
  { label: 'Day', value: '1d' },
  { label: 'Week', value: '1wk' },
  { label: 'Month', value: '1mo' },
];

export default function RulesPage() {
  const [activeTab, setActiveTab] = useState('technical');
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
            Configure the conditions that drive buy and sell signals. Technical
            rules use price-based indicators; fundamental rules use financial
            metrics.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {saving && <span className="spinner"></span>}
          {saved && (
            <span style={{ fontSize: '0.78rem', color: 'var(--green)' }}>✓ Saved</span>
          )}
        </div>
      </div>

      {/* Tab switcher */}
      <div style={{ marginBottom: '24px' }}>
        <FilterTabs tabs={RULE_TABS} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {/* ==============================
          TECHNICAL ANALYSIS TAB
          ============================== */}
      {activeTab === 'technical' && (
        <>
          {/* Driver Parameters */}
          <div className="section-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Driver (EMA Crossover)</span>
            <div style={{ display: 'flex', gap: '4px', background: 'var(--bg-secondary)', padding: '2px', borderRadius: 'var(--radius-sm)' }}>
              <button
                className={`btn ${config.driver_logic === 'and' ? 'btn-primary' : ''}`}
                style={{ padding: '2px 8px', fontSize: '0.7rem', minHeight: 'unset' }}
                onClick={() => handleChange('driver_logic', 'and')}
              >
                AND
              </button>
              <button
                className={`btn ${config.driver_logic === 'or' ? 'btn-primary' : ''}`}
                style={{ padding: '2px 8px', fontSize: '0.7rem', minHeight: 'unset' }}
                onClick={() => handleChange('driver_logic', 'or')}
              >
                OR
              </button>
            </div>
          </div>
          <div className="card" style={{ padding: 0 }}>
            <div className="form-group">
              <div className="form-label-wrap">
                <div className="form-label">Fast EMA period</div>
                <div className="form-hint">Fast moving average (default 11)</div>
              </div>
              <input
                type="number"
                className="form-input"
                value={config.fast_ema_period || ''}
                onChange={(e) => handleChange('fast_ema_period', e.target.value)}
                min="1"
              />
            </div>

            <div className="form-group">
              <div className="form-label-wrap">
                <div className="form-label">Slow EMA period</div>
                <div className="form-hint">Slow moving average (default 50)</div>
              </div>
              <input
                type="number"
                className="form-input"
                value={config.slow_ema_period || ''}
                onChange={(e) => handleChange('slow_ema_period', e.target.value)}
                min="1"
              />
            </div>
          </div>

          {/* Validation Parameters */}
          <div className="section-label">Validation (RSI & Momentum)</div>
          <div className="card" style={{ padding: 0 }}>
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
          </div>

          {/* Timeframe & Data */}
          <div className="section-label">Timeframe &amp; data</div>
          <div className="card" style={{ padding: 0 }}>
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

            <div className="form-group">
              <div className="form-label-wrap">
                <div className="form-label">Price data source</div>
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
      )}

      {/* ==============================
          FUNDAMENTAL ANALYSIS TAB
          ============================== */}
      {activeTab === 'fundamental' && (
        <>
          <div className="section-label">Valuation filters</div>
          <div className="card" style={{ padding: 0 }}>
            <div className="form-group">
              <div className="form-label-wrap">
                <div className="form-label">PE ratio</div>
                <div className="form-hint">Price-to-earnings ratio</div>
              </div>
              <input
                type="number"
                className="form-input"
                value={config.pe_ratio || ''}
                onChange={(e) => handleChange('pe_ratio', e.target.value)}
              />
            </div>

            <div className="form-group">
              <div className="form-label-wrap">
                <div className="form-label">Market cap (in crores)</div>
                <div className="form-hint">Total market value</div>
              </div>
              <input
                type="number"
                className="form-input"
                value={config.market_cap || ''}
                onChange={(e) => handleChange('market_cap', e.target.value)}
              />
            </div>

            <div className="form-group">
              <div className="form-label-wrap">
                <div className="form-label">Market cap to Annual sales ratio</div>
                <div className="form-hint">Valuation multiple</div>
              </div>
              <input
                type="number"
                className="form-input"
                value={config.mcap_sales_ratio || ''}
                onChange={(e) => handleChange('mcap_sales_ratio', e.target.value)}
              />
            </div>
          </div>

          <div className="section-label">Growth & Size filters</div>
          <div className="card" style={{ padding: 0 }}>
            <div className="form-group">
              <div className="form-label-wrap">
                <div className="form-label">Sales growth 3 year CAGR (%)</div>
                <div className="form-hint">3-year annualized revenue growth</div>
              </div>
              <input
                type="number"
                className="form-input"
                value={config.sales_growth_3yr || ''}
                onChange={(e) => handleChange('sales_growth_3yr', e.target.value)}
              />
            </div>

            <div className="form-group">
              <div className="form-label-wrap">
                <div className="form-label">Profit growth 3 year CAGR (%)</div>
                <div className="form-hint">3-year annualized earnings growth</div>
              </div>
              <input
                type="number"
                className="form-input"
                value={config.profit_growth_3yr || ''}
                onChange={(e) => handleChange('profit_growth_3yr', e.target.value)}
              />
            </div>

            <div className="form-group">
              <div className="form-label-wrap">
                <div className="form-label">Annual Sales in crs</div>
                <div className="form-hint">Total revenue (in crores)</div>
              </div>
              <input
                type="number"
                className="form-input"
                value={config.annual_sales || ''}
                onChange={(e) => handleChange('annual_sales', e.target.value)}
              />
            </div>
          </div>
        </>
      )}
    </>
  );
}
