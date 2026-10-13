import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../context/AuthContext';
import { fetchAnalyticsOverview } from '../api/analytics';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import {
  AlertTriangle,
  TrendingDown,
  DollarSign,
  Clock,
  ShieldCheck,
  Flame,
  Activity,
  Filter,
  RotateCcw,
  Layers,
  Building2,
  Globe2,
  CheckCircle2,
  Zap
} from 'lucide-react';

const TRIAGE_COLORS = {
  'P1-Critical': '#ef4444',
  'P2-High': '#f59e0b',
  'P3-Medium': '#3b82f6',
  'P4-Low': '#10b981',
};

const DISRUPTION_COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f97316', '#10b981', '#06b6d4'];
const REGION_COLORS = ['#6366f1', '#3b82f6', '#14b8a6', '#f59e0b', '#ec4899'];

// Custom Dark Tooltip
function ChartTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-900/95 backdrop-blur-md text-white text-xs rounded-lg p-3 shadow-xl border border-slate-700/80 max-w-xs z-50">
      {label && <p className="font-semibold text-slate-200 border-b border-slate-800 pb-1.5 mb-1.5">{label}</p>}
      <div className="space-y-1">
        {payload.map((entry, idx) => (
          <div key={idx} className="flex items-center justify-between gap-3 text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm inline-block" style={{ backgroundColor: entry.color || entry.fill }} />
              <span className="font-medium text-slate-300">{entry.name}:</span>
            </span>
            <span className="font-bold text-white font-mono">
              {formatter ? formatter(entry.value, entry.name) : (typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function DisruptionAnalytics() {
  const { token } = useAuth();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filter states
  const [selectedIndustry, setSelectedIndustry] = useState('All');
  const [selectedRegion, setSelectedRegion] = useState('All');

  const industries = ['All', 'Aerospace', 'Automotive', 'Consumer Goods', 'Electronics', 'Pharmaceuticals'];
  const regions = ['All', 'Asia-Pacific', 'Europe', 'North America', 'Latin America', 'Middle East'];

  const loadData = async (ind = selectedIndustry, reg = selectedRegion, forceRefresh = false) => {
    setLoading(true);
    setError('');
    try {
      const res = await fetchAnalyticsOverview({
        industry: ind,
        region: reg,
        token,
        bypassCache: forceRefresh,
      });
      setData(res);
    } catch (err) {
      console.error('Failed to load disruption analytics:', err);
      setError(err.message || 'Failed to load analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedIndustry, selectedRegion);
  }, [selectedIndustry, selectedRegion]);

  const handleResetFilters = () => {
    setSelectedIndustry('All');
    setSelectedRegion('All');
  };

  // Pre-formatted chart datasets
  const severityBackupData = useMemo(() => {
    if (!data?.severity_backup_comparison) return [];
    // Transform into { severity: 1, withBackupImpact: 14.2, withoutBackupImpact: 22.4, ... }
    const grouped = {};
    for (const item of data.severity_backup_comparison) {
      const s = `Sev ${item.severity}`;
      if (!grouped[s]) {
        grouped[s] = { severityLabel: s, severity: item.severity };
      }
      if (item.has_backup_supplier) {
        grouped[s].withBackupDowntime = item.avg_impact_pct;
        grouped[s].withBackupRecovery = item.avg_recovery_days;
      } else {
        grouped[s].noBackupDowntime = item.avg_impact_pct;
        grouped[s].noBackupRecovery = item.avg_recovery_days;
      }
    }
    return Object.values(grouped).sort((a, b) => a.severity - b.severity);
  }, [data]);

  const kpis = data?.kpis;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header and Filter Controls */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm p-5 sm:p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 bg-slate-100 text-slate-800 rounded-lg">
                <Layers className="w-4 h-4" />
              </span>
              <h2 className="text-lg font-bold text-slate-950">Supply Chain Disruption Analytics</h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Multi-dimensional cohort analysis across 100,000 incident records, financial impacts, and mitigation velocity.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {(selectedIndustry !== 'All' || selectedRegion !== 'All') && (
              <button
                onClick={handleResetFilters}
                className="flex items-center gap-1.5 text-xs text-rose-600 hover:text-rose-700 font-semibold px-2.5 py-1.5 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset Filters</span>
              </button>
            )}
            <button
              onClick={() => loadData(selectedIndustry, selectedRegion, true)}
              disabled={loading}
              className="flex items-center gap-1.5 text-xs text-slate-700 hover:text-slate-900 font-semibold px-3 py-1.5 border border-slate-200 hover:border-slate-300 rounded-lg transition-colors bg-white shadow-2xs"
            >
              <Activity className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-slate-400' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Filter Dropdowns */}
        <div className="pt-4 flex flex-wrap items-center gap-4 text-xs">
          <div className="flex items-center gap-2 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
            <Filter className="w-3.5 h-3.5" />
            <span>Filter Cohort:</span>
          </div>

          {/* Industry Filter */}
          <div className="flex items-center gap-1.5">
            <Building2 className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:ring-1 focus:ring-slate-900 focus:outline-hidden"
            >
              {industries.map((ind) => (
                <option key={ind} value={ind}>
                  Industry: {ind}
                </option>
              ))}
            </select>
          </div>

          {/* Region Filter */}
          <div className="flex items-center gap-1.5">
            <Globe2 className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:ring-1 focus:ring-slate-900 focus:outline-hidden"
            >
              {regions.map((reg) => (
                <option key={reg} value={reg}>
                  Region: {reg}
                </option>
              ))}
            </select>
          </div>

          {data?.query_time_ms && (
            <span className="text-[11px] text-slate-400 ml-auto font-mono">
              Aggregated in {data.query_time_ms}ms
            </span>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs font-medium">
          {error}
        </div>
      )}

      {/* Top KPI StatCards Banner */}
      {kpis && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5 sm:gap-4">
          {/* 1. Total Incidents */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1.5">
              <span className="text-xs font-medium">Disruptions</span>
              <AlertTriangle className="w-4 h-4 text-slate-400" />
            </div>
            <p className="text-xl sm:text-2xl font-extrabold text-slate-950 font-mono tracking-tight">
              {kpis.total_incidents.toLocaleString()}
            </p>
            <p className="text-[11px] text-slate-500 mt-1">Filtered cohort count</p>
          </div>

          {/* 2. Mean Downtime */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1.5">
              <span className="text-xs font-medium">Avg Downtime</span>
              <TrendingDown className="w-4 h-4 text-amber-500" />
            </div>
            <p className="text-xl sm:text-2xl font-extrabold text-slate-950 font-mono tracking-tight">
              {kpis.avg_production_impact_pct}%
            </p>
            <p className="text-[11px] text-amber-600 font-medium mt-1">Line stoppage rate</p>
          </div>

          {/* 3. Mean Revenue Loss */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1.5">
              <span className="text-xs font-medium">Mean Loss</span>
              <DollarSign className="w-4 h-4 text-rose-500" />
            </div>
            <p className="text-xl sm:text-2xl font-extrabold text-slate-950 font-mono tracking-tight">
              ${(kpis.avg_revenue_loss_usd / 1e6).toFixed(2)}M
            </p>
            <p className="text-[11px] text-slate-500 mt-1">
              Total: ${(kpis.total_revenue_loss_usd / 1e9).toFixed(1)}B
            </p>
          </div>

          {/* 4. Mean Recovery Horizon */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1.5">
              <span className="text-xs font-medium">Avg Recovery</span>
              <Clock className="w-4 h-4 text-blue-500" />
            </div>
            <p className="text-xl sm:text-2xl font-extrabold text-slate-950 font-mono tracking-tight">
              {kpis.avg_recovery_days} <span className="text-xs font-normal text-slate-500">days</span>
            </p>
            <p className="text-[11px] text-slate-500 mt-1">To 100% restoration</p>
          </div>

          {/* 5. Network Resilience Index */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1.5">
              <span className="text-xs font-medium">Resilience Index</span>
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
            </div>
            <p className="text-xl sm:text-2xl font-extrabold text-emerald-600 font-mono tracking-tight">
              {kpis.avg_resilience_score}%
            </p>
            <p className="text-[11px] text-slate-500 mt-1">{kpis.backup_supplier_pct}% dual-sourced</p>
          </div>

          {/* 6. P1 Critical Count */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1.5">
              <span className="text-xs font-medium">P1 Critical</span>
              <Flame className="w-4 h-4 text-rose-600" />
            </div>
            <p className="text-xl sm:text-2xl font-extrabold text-rose-600 font-mono tracking-tight">
              {kpis.p1_critical_count.toLocaleString()}
            </p>
            <p className="text-[11px] text-rose-600 font-semibold mt-1">
              {((kpis.p1_critical_count / kpis.total_incidents) * 100).toFixed(1)}% triage load
            </p>
          </div>
        </div>
      )}

      {/* Charts Grid */}
      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart 1: Disruption Type Breakdown */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-slate-900">Disruption Taxonomy Impact & Incident Volume</h3>
              <p className="text-xs text-slate-500">Incident frequency and average financial loss across taxonomy types.</p>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.disruption_type_distribution} margin={{ top: 10, right: 10, left: -10, bottom: 25 }}>
                  <CartesianGrid vertical={false} stroke="#f1f5f9" />
                  <XAxis
                    dataKey="disruption_type"
                    tick={{ fontSize: 10, fill: '#64748b' }}
                    angle={-20}
                    textAnchor="end"
                    interval={0}
                    stroke="#cbd5e1"
                  />
                  <YAxis
                    tick={{ fontSize: 10, fill: '#64748b' }}
                    stroke="#cbd5e1"
                    tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    content={<ChartTooltip formatter={(val, name) => (name === 'Volume' ? val.toLocaleString() : `$${(val / 1e6).toFixed(2)}M`)} />}
                  />
                  <Bar dataKey="count" name="Volume" fill="#0284c7" radius={[4, 4, 0, 0]} maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Riskiest: <strong className="text-slate-800">Cyber Attack</strong> ($3.37M avg)</span>
              <span>Highest frequency: <strong className="text-slate-800">Port Congestion</strong> (25.1k)</span>
            </div>
          </div>

          {/* Chart 2: Industry Exposure & Financial Loss */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-slate-900">Industry Exposure & Mean Downtime</h3>
              <p className="text-xs text-slate-500">Average revenue exposure ($M) and production downtime percentage by sector.</p>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.industry_exposure} margin={{ top: 10, right: 10, left: -5, bottom: 15 }}>
                  <CartesianGrid vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="industry" tick={{ fontSize: 10, fill: '#64748b' }} stroke="#cbd5e1" />
                  <YAxis
                    tick={{ fontSize: 10, fill: '#64748b' }}
                    stroke="#cbd5e1"
                    tickFormatter={(v) => `$${(v / 1e6).toFixed(1)}M`}
                  />
                  <Tooltip
                    content={<ChartTooltip formatter={(val, name) => (name.includes('Loss') ? `$${(val / 1e6).toFixed(2)}M` : `${val}%`)} />}
                  />
                  <Bar dataKey="avg_revenue_loss_usd" name="Avg Loss ($)" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Top loss sector: <strong className="text-slate-800">Electronics & Aerospace</strong></span>
              <span>Typical impact: <strong className="text-slate-800">~31.4% downtime</strong></span>
            </div>
          </div>

          {/* Chart 3: Backup Supplier Mitigation Shield */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Backup Supplier Shield vs. Single Sourcing</h3>
                <p className="text-xs text-slate-500">Production downtime (%) across severity levels: Dual-sourced vs. Single-source.</p>
              </div>
              <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                <ShieldCheck className="w-3 h-3" />
                -18.6d Recovery
              </span>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityBackupData} margin={{ top: 10, right: 10, left: -15, bottom: 15 }}>
                  <CartesianGrid vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="severityLabel" tick={{ fontSize: 10, fill: '#64748b' }} stroke="#cbd5e1" />
                  <YAxis tick={{ fontSize: 10, fill: '#64748b' }} unit="%" stroke="#cbd5e1" />
                  <Tooltip content={<ChartTooltip formatter={(val) => `${val}% downtime`} />} />
                  <Legend wrapperStyle={{ fontSize: 11, paddingTop: 6 }} />
                  <Bar dataKey="withBackupDowntime" name="With Backup Supplier" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={28} />
                  <Bar dataKey="noBackupDowntime" name="Single-Source (No Backup)" fill="#f43f5e" radius={[4, 4, 0, 0]} maxBarSize={28} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-[11px] text-slate-500 mt-2">
              Suppliers with qualified secondary backups exhibit significantly contained downtime, especially during Severity 4–5 incidents.
            </p>
          </div>

          {/* Chart 4: Triage Priority Distribution (Donut) */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-slate-900">Resilience Triage Priority Breakdown</h3>
              <p className="text-xs text-slate-500">Proportion of incidents routed into P1-Critical through P4-Low queues.</p>
            </div>
            <div className="flex flex-col sm:flex-row items-center justify-around h-64">
              <div className="w-full sm:w-1/2 h-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.triage_distribution}
                      dataKey="count"
                      nameKey="prioritization_level"
                      innerRadius={55}
                      outerRadius={85}
                      paddingAngle={3}
                      strokeWidth={0}
                    >
                      {data.triage_distribution.map((entry) => (
                        <Cell key={entry.prioritization_level} fill={TRIAGE_COLORS[entry.prioritization_level] || '#94a3b8'} />
                      ))}
                    </Pie>
                    <Tooltip content={<ChartTooltip formatter={(val) => `${val.toLocaleString()} incidents`} />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Legend with percentages */}
              <div className="w-full sm:w-1/2 space-y-2.5 pl-4">
                {data.triage_distribution.map((entry) => (
                  <div key={entry.prioritization_level} className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-2">
                      <span
                        className="w-3 h-3 rounded-xs shrink-0"
                        style={{ backgroundColor: TRIAGE_COLORS[entry.prioritization_level] || '#94a3b8' }}
                      />
                      <span className="font-semibold text-slate-800">{entry.prioritization_level}</span>
                    </span>
                    <span className="font-mono text-slate-600 font-bold">
                      {entry.count.toLocaleString()} <span className="text-[10px] text-slate-400 font-normal">({entry.percentage}%)</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>
            <p className="text-[11px] text-slate-500 mt-2">
              Incidents classified as P1-Critical activate automated crisis alerts and priority supplier buffer reservations.
            </p>
          </div>

          {/* Chart 5: Response Strategy Recovery Efficiency */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-slate-900">Response Strategy Recovery Velocity</h3>
              <p className="text-xs text-slate-500">Average resolution timeline (days) and response initiation speed by strategy.</p>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.response_effectiveness} layout="vertical" margin={{ top: 5, right: 20, left: 25, bottom: 5 }}>
                  <CartesianGrid horizontal={false} stroke="#f1f5f9" />
                  <XAxis type="number" unit="d" tick={{ fontSize: 10, fill: '#64748b' }} stroke="#cbd5e1" />
                  <YAxis type="category" dataKey="strategy" tick={{ fontSize: 10, fill: '#475569' }} width={110} stroke="#cbd5e1" />
                  <Tooltip content={<ChartTooltip formatter={(val, name) => `${val} days`} />} />
                  <Legend wrapperStyle={{ fontSize: 11, paddingTop: 4 }} />
                  <Bar dataKey="avg_recovery_days" name="Full Recovery Days" fill="#0284c7" radius={[0, 4, 4, 0]} maxBarSize={20} />
                  <Bar dataKey="avg_response_time_days" name="Response Activation SLA" fill="#f59e0b" radius={[0, 4, 4, 0]} maxBarSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Fastest strategy: <strong className="text-emerald-700">Alternative Supplier</strong> (~62.8 days)</span>
              <span>Longest: <strong className="text-slate-800">Combined Strategy</strong> (~108 days)</span>
            </div>
          </div>

          {/* Chart 6: Regional Risk Profile & Disruption Heat */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-slate-900">Regional Disruption Heat & Resilience</h3>
              <p className="text-xs text-slate-500">Disruption frequency and mean resilience index across key trade corridors.</p>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.regional_breakdown} margin={{ top: 10, right: 10, left: -10, bottom: 15 }}>
                  <CartesianGrid vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="region" tick={{ fontSize: 10, fill: '#64748b' }} stroke="#cbd5e1" />
                  <YAxis tick={{ fontSize: 10, fill: '#64748b' }} stroke="#cbd5e1" tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                  <Tooltip content={<ChartTooltip formatter={(val, name) => (name === 'Disruptions' ? val.toLocaleString() : `${val}%`)} />} />
                  <Legend wrapperStyle={{ fontSize: 11, paddingTop: 4 }} />
                  <Bar dataKey="count" name="Disruptions" fill="#8b5cf6" radius={[4, 4, 0, 0]} maxBarSize={36} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Top region by volume: <strong className="text-slate-800">Asia-Pacific & Europe</strong></span>
              <span>Resilience average: <strong className="text-slate-800">~79.5%</strong></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
