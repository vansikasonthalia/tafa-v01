'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  {
    href: '/',
    title: 'Stocklist',
    subtitle: 'Upload & manage universe',
  },
  {
    href: '/recommendations',
    title: 'Recommendations',
    subtitle: 'Buy / sell signals log',
  },
  {
    href: '/approvals',
    title: 'Approvals',
    subtitle: 'Review before an order fires',
  },
  {
    href: '/zerodha',
    title: 'Zerodha',
    subtitle: 'Connect Kite Connect',
  },
  {
    href: '/rules',
    title: 'Rules',
    subtitle: 'Thresholds & timeframe',
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-tags">
          <span className="sidebar-brand-tag">RSI</span>
          <span className="sidebar-brand-tag">EMA</span>
          <span className="sidebar-brand-tag">WMA</span>
        </div>
        <h1>Screener</h1>
        <p>Technical + fundamental scan</p>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const isActive =
            item.href === '/'
              ? pathname === '/'
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
            >
              <div className="sidebar-nav-item-title">{item.title}</div>
              <div className="sidebar-nav-item-sub">{item.subtitle}</div>
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <p>Data via Yahoo Finance. Signals are informational, not advice.</p>
      </div>
    </aside>
  );
}
