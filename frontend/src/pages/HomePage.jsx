import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const [health, setHealth] = useState(null);
  const [loadingHealth, setLoadingHealth] = useState(true);

  useEffect(() => {
    fetch('/health')
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch((err) => console.error('Health check failed:', err))
      .finally(() => setLoadingHealth(false));
  }, []);

  const online = health?.status === 'healthy';

  const status = [
    {
      label: 'API',
      value: loadingHealth ? 'Checking…' : online ? 'Online' : 'Offline',
      dot: loadingHealth ? 'bg-neutral-300' : online ? 'bg-emerald-500' : 'bg-red-500',
    },
    {
      label: 'Warehouse',
      value: loadingHealth ? 'Loading…' : `${(health?.total_records || 100000).toLocaleString()} records`,
    },
    {
      label: 'Models',
      value: loadingHealth ? '3 models' : `${health?.models_loaded?.length || 3} XGBoost loaded`,
    },
  ];

  const pillars = [
    {
      title: 'Five-agent pipeline',
      body: 'Investigation, impact assessment, response planning, recovery roadmap and an LLM judge produce an executive dossier in under two seconds.',
    },
    {
      title: 'Explainable forecasts',
      body: 'Chained XGBoost models predict production downtime and revenue loss. TreeSHAP shows which factors drive each prediction.',
    },
    {
      title: 'Grounded SQL',
      body: 'Natural-language questions are checked against a controlled knowledge graph, so generated queries stay read-only and on-schema.',
    },
  ];

  return (
    <div className="flex-1">
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 md:pt-24 md:pb-20">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-800 mb-6">
          <span className="w-2 h-2 rounded-full bg-blue-600"></span>
          <span>Synapt Trident MCP • 5-Agent Crisis Response Engine</span>
        </div>

        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight leading-[1.12] text-slate-950 max-w-3xl">
          Triage supply chain disruptions with evidence, not guesswork.
        </h1>
        <p className="mt-6 text-base md:text-lg text-slate-600 max-w-2xl leading-relaxed">
          Search 100,000 historical incidents, forecast the impact of a new one, and inspect exactly
          why the model reached its conclusion.
        </p>

        <div className="mt-9 flex flex-wrap items-center gap-3">
          <Link
            to={isAuthenticated ? '/dashboard' : '/login'}
            className="bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 rounded-lg transition-colors text-sm font-semibold shadow-sm"
          >
            {isAuthenticated ? 'Open dashboard' : 'Sign in to start'}
          </Link>
          <Link
            to="/instructions"
            className="text-slate-700 hover:text-slate-950 border border-slate-300 hover:border-slate-800 px-5 py-2.5 rounded-lg transition-colors text-sm font-semibold"
          >
            Read the guide
          </Link>
        </div>

        <dl className="mt-14 flex flex-wrap gap-x-10 gap-y-4 border-t border-slate-200/80 pt-5 text-xs sm:text-sm">
          {status.map((s) => (
            <div key={s.label} className="flex items-center gap-2">
              <dt className="text-slate-500 font-medium">{s.label}</dt>
              <dd className="flex items-center gap-2 font-semibold text-slate-900 font-mono">
                {s.dot && <span className={`w-2 h-2 rounded-full ${s.dot}`} aria-hidden="true"></span>}
                {s.value}
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="border-t border-slate-200/80 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-12">
          {pillars.map((p) => (
            <div key={p.title} className="p-6 rounded-xl border border-slate-100 hover:border-slate-200 transition-colors bg-slate-50/30">
              <h2 className="text-base font-bold text-slate-950 mb-2">{p.title}</h2>
              <p className="text-sm text-slate-600 leading-relaxed">{p.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-slate-200/80 bg-slate-50/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-xs text-slate-600">
          User accounts live in an isolated SQLite store (<code className="text-slate-900 font-mono font-semibold">auth.db</code>).
          Disruption data lives in MySQL (<code className="text-slate-900 font-mono font-semibold">v_disruption_details</code>).
          The two never mix.
        </div>
      </section>
    </div>
  );
}
