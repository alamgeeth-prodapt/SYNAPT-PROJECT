import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Search,
  Terminal,
  Database,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Play,
  Layers,
  ArrowRight
} from 'lucide-react';

export default function SQLConsole() {
  const { token } = useAuth();

  const [query, setQuery] = useState('Show me factory fire disruptions in Automotive without backup supplier');
  const [limit, setLimit] = useState(15);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const sampleQueries = [
    'Show me factory fire disruptions in Automotive without backup supplier',
    'Find severe cyber attacks affecting Tier 1 electronics suppliers in Asia-Pacific',
    'List port congestion incidents where recovery took more than 60 days',
    'Top disruptions by revenue loss in Aerospace with large suppliers',
  ];

  const handleExecute = async (queryToRun = query) => {
    if (!queryToRun.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch('/api/v1/query-sql', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: queryToRun,
          limit: Number(limit),
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'SQL synthesis failed' }));
        throw new Error(err.detail || 'Execution error');
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to execute query');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleExecute(query);
  };

  return (
    <div className="bg-white border border-neutral-200 rounded-lg p-6 space-y-6">
      
      {/* Header */}
      <div className="border-b border-neutral-200 pb-4">
        <h2 className="text-lg font-semibold text-neutral-900">SQL assistant</h2>
        <p className="text-xs text-neutral-500 mt-0.5">
          Ask questions in plain English. Queries are read-only and checked against the knowledge graph.
        </p>
      </div>

      {/* Sample Query Chips */}
      <div className="space-y-2">
        <span className="text-xs text-neutral-500">Sample Inquiries:</span>
        <div className="flex flex-wrap gap-2">
          {sampleQueries.map((sq, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setQuery(sq);
                handleExecute(sq);
              }}
              className="text-xs bg-neutral-50 hover:bg-neutral-100 text-neutral-700 border border-neutral-200 px-3 py-1.5 rounded-md transition-colors text-left"
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Query Bar */}
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Show severe cyber attacks on electronics suppliers in APAC..."
            className="w-full bg-slate-50/70 border border-slate-200 rounded-lg pl-10 pr-4 py-2.5 text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900/10"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3 pointer-events-none" />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="bg-slate-50/70 border border-slate-200 rounded-lg px-3 py-2.5 text-xs text-slate-700 focus:outline-none focus:border-slate-900"
          >
            <option value="5">Limit 5</option>
            <option value="15">Limit 15</option>
            <option value="25">Limit 25</option>
            <option value="50">Limit 50</option>
          </select>

          <button
            type="submit"
            disabled={loading}
            className="flex-1 sm:flex-none flex items-center justify-center space-x-2 bg-slate-900 hover:bg-slate-800 text-white font-medium px-5 py-2.5 rounded-lg shadow-sm transition-all disabled:opacity-50 text-xs sm:text-sm"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{loading ? 'Synthesizing...' : 'Execute SQL'}</span>
          </button>
        </div>
      </form>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Results View */}
      {result && (
        <div className="space-y-4 pt-2">
          
          {/* Metadata pill bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-slate-50/80 rounded-lg border border-slate-200 text-xs">
            <div className="flex items-center space-x-3 text-slate-500">
              <span>Rows Returned: <strong className="text-slate-900 font-mono">{result.row_count}</strong></span>
              <span>•</span>
              <span>Execution Time: <strong className="text-slate-900 font-mono">{result.execution_time_ms.toFixed(1)} ms</strong></span>
              <span>•</span>
              <span>Injected Classes: <strong className="text-slate-700 font-mono">{result.injected_classes_count}</strong></span>
            </div>
            <span className="text-[10px] bg-slate-100 text-slate-800 border border-slate-300 px-2.5 py-0.5 rounded-full font-mono font-medium">
              Safe Read-Only Guardrail Verified
            </span>
          </div>

          {/* Generated SQL snippet */}
          <div className="space-y-1">
            <span className="text-[11px] font-semibold text-neutral-500">
              Synthesized SQL Statement (v_disruption_details):
            </span>
            <pre className="p-3 bg-neutral-50 rounded-md border border-neutral-200 text-xs font-mono text-neutral-700 overflow-x-auto">
              {result.generated_sql}
            </pre>
          </div>

          {/* Data Table */}
          {result.records && result.records.length > 0 ? (
            <div className="border border-neutral-200 rounded-md overflow-hidden bg-neutral-50">
              <div className="overflow-x-auto max-h-80">
                <table className="w-full text-left text-xs whitespace-nowrap">
                  <thead className="bg-white text-neutral-500 border-b border-neutral-200 sticky top-0 font-semibold text-[11px]">
                    <tr>
                      {result.columns.map((col) => (
                        <th key={col} className="py-2.5 px-3">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-100 font-mono text-neutral-700">
                    {result.records.map((row, idx) => (
                      <tr key={idx} className="hover:bg-neutral-50 transition-colors">
                        {result.columns.map((col) => (
                          <td key={col} className="py-2 px-3 text-[11px]">
                            {typeof row[col] === 'number'
                              ? Number.isInteger(row[col])
                                ? row[col]
                                : Number(row[col]).toFixed(2)
                              : String(row[col] ?? '')}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="p-6 bg-neutral-50 rounded-md border border-neutral-200 text-center text-xs text-neutral-500">
              Query executed successfully, but returned zero matching records.
            </div>
          )}

        </div>
      )}

    </div>
  );
}
