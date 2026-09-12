import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata = {
  title: 'TAFA — Stock Screener',
  description: 'Technical + fundamental stock screener with RSI, EMA, WMA indicators and Zerodha integration.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="app-layout">
          <Sidebar />
          <main className="main-content">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
