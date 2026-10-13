/**
 * Analytics API Client
 * Fetches pre-aggregated supply chain disruption analytics from FastAPI backend.
 * Features in-memory caching and request deduplication for ultra-fast dashboard loading.
 */

const _clientCache = new Map();
const _inFlightRequests = new Map();
const CACHE_TTL_MS = 15 * 60 * 1000; // 15 minutes

export async function fetchAnalyticsOverview({ industry = '', region = '', token = '', bypassCache = false } = {}) {
  const indKey = industry && industry !== 'All' ? industry.trim().toLowerCase() : 'all';
  const regKey = region && region !== 'All' ? region.trim().toLowerCase() : 'all';
  const cacheKey = `${indKey}_${regKey}`;

  const now = Date.now();
  if (!bypassCache && _clientCache.has(cacheKey)) {
    const entry = _clientCache.get(cacheKey);
    if (now - entry.timestamp < CACHE_TTL_MS) {
      return entry.data;
    }
  }

  // Deduplicate in-flight requests for identical cacheKey
  if (!bypassCache && _inFlightRequests.has(cacheKey)) {
    return _inFlightRequests.get(cacheKey);
  }

  const params = new URLSearchParams();
  if (industry && industry !== 'All') params.append('industry', industry);
  if (region && region !== 'All') params.append('region', region);

  const headers = { 'Content-Type': 'application/json' };
  const effectiveToken = token || localStorage.getItem('token');
  if (effectiveToken) {
    headers['Authorization'] = `Bearer ${effectiveToken}`;
  }

  const queryStr = params.toString() ? `?${params.toString()}` : '';

  const fetchPromise = (async () => {
    try {
      const response = await fetch(`/api/v1/analytics/overview${queryStr}`, { headers });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Analytics API error (${response.status}): ${errorText}`);
      }

      const data = await response.json();
      _clientCache.set(cacheKey, { data, timestamp: Date.now() });
      return data;
    } finally {
      _inFlightRequests.delete(cacheKey);
    }
  })();

  _inFlightRequests.set(cacheKey, fetchPromise);
  return fetchPromise;
}

export function prefetchAnalyticsOverview({ token = '' } = {}) {
  fetchAnalyticsOverview({ token }).catch(() => {});
}

export function clearAnalyticsClientCache() {
  _clientCache.clear();
}
