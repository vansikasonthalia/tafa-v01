'use client';

export default function ZerodhaPage() {
  return (
    <>
      <div className="page-header">
        <div className="page-header-text">
          <h2>Zerodha</h2>
          <p>
            Connect Kite Connect to pull live/historical data and to place orders
            you approve from the Approvals tab. Nothing is ever sent to your
            broker automatically.
          </p>
        </div>
      </div>

      <div className="placeholder-banner">
        <span className="placeholder-banner-icon">🔧</span>
        <span>
          Zerodha integration is coming soon. This page is a placeholder for
          connecting your Kite Connect API credentials.
        </span>
      </div>

      {/* API Credentials Section */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <div>
            <div className="card-title">1. API credentials</div>
            <div className="card-subtitle" style={{ marginTop: '4px' }}>
              From developers.kite.trade → My Apps → your app. Set the app&apos;s
              Redirect URL to <code style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.75rem',
                background: 'rgba(255,255,255,0.06)',
                padding: '2px 6px',
                borderRadius: '4px',
              }}>http://localhost:8000/api/kite/callback</code>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <input
            type="text"
            placeholder="API key"
            className="form-input form-input-wide"
            disabled
            style={{ flex: 1, textAlign: 'left' }}
          />
          <input
            type="password"
            placeholder="API secret"
            className="form-input form-input-wide"
            disabled
            style={{ flex: 1, textAlign: 'left' }}
          />
        </div>

        <button className="btn btn-secondary" disabled>
          Save credentials
        </button>
      </div>

      {/* Daily Login Section */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">2. Daily login</div>
            <div className="card-subtitle" style={{ marginTop: '4px' }}>
              Kite access tokens expire every day — you&apos;ll do this once each
              morning before running the screener.
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="badge" style={{
            background: 'var(--red-muted)',
            color: 'var(--red)',
          }}>
            Not connected
          </span>
          <button className="btn btn-secondary" disabled>
            Connect
          </button>
        </div>
      </div>
    </>
  );
}
