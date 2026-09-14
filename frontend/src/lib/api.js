/**
 * API client for the TAFA backend.
 * Base URL: http://localhost:8000
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error: ${res.status}`);
  }

  return res.json();
}

// --- Watchlist ---

export async function uploadWatchlist(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/watchlist/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || 'Upload failed');
  }

  return res.json();
}

export async function getWatchlist() {
  return request('/api/watchlist');
}

export async function clearWatchlist() {
  return request('/api/watchlist', { method: 'DELETE' });
}

export async function removeTicker(ticker) {
  return request(`/api/watchlist/${ticker}`, { method: 'DELETE' });
}

// --- Config ---

export async function getConfig() {
  return request('/api/config');
}

export async function updateConfig(updates) {
  return request('/api/config', {
    method: 'POST',
    body: JSON.stringify(updates),
  });
}

// --- Screener ---

export async function runScreener() {
  return request('/api/screener/run', { method: 'POST' });
}

export async function getScreenerStatus() {
  return request('/api/screener/status');
}

// --- Tracking ---

export async function getTrackingEntries(signal = null) {
  const params = signal ? `?signal=${signal}` : '';
  return request(`/api/tracking${params}`);
}

export async function deleteTrackingEntry(entryId) {
  return request(`/api/tracking/${entryId}`, { method: 'DELETE' });
}

// --- Health ---

export async function getHealth() {
  return request('/api/health');
}
