import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Activity,
  ArrowRight,
  TrendingDown,
  Shield,
  AlertTriangle,
  RotateCcw
} from 'lucide-react';

export default function DisruptionsTable({ onSelectIncident }) {
  const { token } = useAuth();

  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 25; // 25 records per page as requested

  // Filter states
  const [search, setSearch] = useState('');
  const [disruptionType, setDisruptionType] = useState('');
  const [industry, setIndustry] = useState('');
  const [severity, setSeverity] = useState('');
  const [supplierRegion, setSupplierRegion] = useState('');

  const fetchDisruptions = async (page = 1) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });

      if (search.trim()) params.append('search', search.trim());
      if (disruptionType) params.append('disruption_type', disruptionType);
      if (industry) params.append('industry', industry);
      if (severity) params.append('severity', severity);
      if (supplierRegion) params.append('supplier_region', supplierRegion);

      const res = await fetch(`/api/v1/disruptions?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!res.ok) throw new Error('Failed to load records');

      const data = await res.json();
      setRecords(data.records || []);
      setTotalRecords(data.total_records || 0);
      setTotalPages(data.total_pages || 1);
      setCurrentPage(data.page || 1);
    } catch (err) {
      console.error('Error fetching disruptions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDisruptions(1);
  }, [disruptionType, industry, severity, supplierRegion]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchDisruptions(1);
  };

  const handleResetFilters = () => {
    setSearch('');
    setDisruptionType('');
    setIndustry('');
    setSeverity('');
    setSupplierRegion('');
    fetchDisruptions(1);
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      fetchDisruptions(newPage);
      window.scrollTo({ top: 300, behavior: 'smooth' });
    }
  };

  const getPriorityBadge = (level) => {
    switch (level) {
      case 'P1-Critical':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'P2-High':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'P3-Medium':
        return 'bg-neutral-100 text-neutral-700 border-neutral-200';
      case 'P4-Low':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      default:
        return 'bg-neutral-100 text-neutral-500 border-neutral-300';
    }
  };

  const formatCurrency = (val) => {
    if (val >= 1000000) {
      return `$${(val / 1000000).toFixed(2)}M`;
    }
    if (val >= 1000) {
      return `$${(val / 1000).toFixed(0)}k`;
    }
    return `$${Number(val || 0).toLocaleString()}`;
  };

  return (
    <div className="bg-white border border-slate-200/90 rounded-xl p-6 space-y-6 shadow-sm">
      
      {/* Table Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200/80 pb-5">
        <div>
          <h2 className="text-lg font-bold text-slate-950">Disruption History</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Previously recorded incidents from MySQL warehouse (25 per page). Click Analyze to load into the 5-Agent pipeline.
          </p>
        </div>

        {/* Global Summary Stats */}
        <div className="flex items-center space-x-3 text-xs">
          <span className="text-slate-500">
            Total records: <strong className="text-slate-950 font-mono font-bold">{totalRecords.toLocaleString()}</strong>
          </span>
          <span className="text-slate-500">
            Page <strong className="text-slate-950 font-mono font-bold">{currentPage}</strong> of{' '}
            <strong className="text-slate-950 font-mono font-bold">{totalPages.toLocaleString()}</strong>
          </span>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
        
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="md:col-span-2 relative">
          <input
            type="text"
            placeholder="Search ID, type, industry..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-neutral-50 border border-neutral-200 rounded-md pl-9 pr-4 py-2 text-xs text-neutral-800 placeholder-neutral-400 focus:outline-none focus:border-neutral-900"
          />
          <Search className="w-3.5 h-3.5 text-neutral-500 absolute left-3 top-3 pointer-events-none" />
        </form>

        {/* Disruption Type */}
        <select
          value={disruptionType}
          onChange={(e) => setDisruptionType(e.target.value)}
          className="bg-neutral-50 border border-neutral-200 rounded-md px-3 py-2 text-xs text-neutral-700 focus:outline-none focus:border-neutral-900"
        >
          <option value="">All Disruption Types</option>
          <option value="Factory Incident">Factory Incident</option>
          <option value="Cyber Attack">Cyber Attack</option>
          <option value="Port Congestion">Port Congestion</option>
          <option value="Labor Strike">Labor Strike</option>
          <option value="Geopolitical">Geopolitical</option>
          <option value="Natural Disaster">Natural Disaster</option>
        </select>

        {/* Industry */}
        <select
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="bg-neutral-50 border border-neutral-200 rounded-md px-3 py-2 text-xs text-neutral-700 focus:outline-none focus:border-neutral-900"
        >
          <option value="">All Industries</option>
          <option value="Electronics">Electronics</option>
          <option value="Automotive">Automotive</option>
          <option value="Pharmaceuticals">Pharmaceuticals</option>
          <option value="Consumer Goods">Consumer Goods</option>
          <option value="Aerospace">Aerospace</option>
          <option value="Energy">Energy</option>
        </select>

        {/* Severity */}
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="bg-neutral-50 border border-neutral-200 rounded-md px-3 py-2 text-xs text-neutral-700 focus:outline-none focus:border-neutral-900"
        >
          <option value="">All Severities</option>
          <option value="1">Severity 1 (Minor)</option>
          <option value="2">Severity 2 (Moderate)</option>
          <option value="3">Severity 3 (Significant)</option>
          <option value="4">Severity 4 (Major)</option>
          <option value="5">Severity 5 (Catastrophic)</option>
        </select>

        {/* Reset / Actions */}
        <div className="flex items-center space-x-2">
          <select
            value={supplierRegion}
            onChange={(e) => setSupplierRegion(e.target.value)}
            className="w-full bg-neutral-50 border border-neutral-200 rounded-md px-2.5 py-2 text-xs text-neutral-700 focus:outline-none focus:border-neutral-900"
          >
            <option value="">All Regions</option>
            <option value="Asia-Pacific">Asia-Pacific</option>
            <option value="North America">North America</option>
            <option value="Europe">Europe</option>
            <option value="South America">South America</option>
            <option value="Africa/Middle East">Africa/Middle East</option>
            <option value="Middle East">Middle East</option>
            <option value="Latin America">Latin America</option>
          </select>
          <button
            onClick={handleResetFilters}
            title="Reset Filters"
            className="p-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-md transition-colors shrink-0"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>

      {/* Disruption Records Table */}
      <div className="border border-neutral-200 rounded-md overflow-hidden bg-neutral-50">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs whitespace-nowrap">
            <thead className="bg-white text-neutral-500 border-b border-neutral-200 font-semibold text-[11px]">
              <tr>
                <th className="py-3 px-3.5">ID</th>
                <th className="py-3 px-3.5">Disruption Type</th>
                <th className="py-3 px-3.5">Industry</th>
                <th className="py-3 px-3">Tier</th>
                <th className="py-3 px-3.5">Region</th>
                <th className="py-3 px-3">Sev</th>
                <th className="py-3 px-3 text-center">Backup</th>
                <th className="py-3 px-3.5 text-right">Impact %</th>
                <th className="py-3 px-3.5 text-right">Loss ($)</th>
                <th className="py-3 px-3 text-center">Days</th>
                <th className="py-3 px-3.5 text-center">Resilience</th>
                <th className="py-3 px-3.5 text-center">Triage</th>
                <th className="py-3 px-3.5 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100 text-neutral-700 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={13} className="py-12 text-center text-neutral-500 font-sans">
                    <Activity className="w-5 h-5 animate-spin mx-auto text-neutral-500 mb-2" />
                    <span>Loading 25 disruption records from MySQL warehouse...</span>
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan={13} className="py-12 text-center text-neutral-500 font-sans">
                    No historical disruptions matched your filter criteria.
                  </td>
                </tr>
              ) : (
                records.map((r) => (
                  <tr key={r.disruption_id} className="hover:bg-neutral-50 transition-colors">
                    <td className="py-2.5 px-3.5 text-neutral-700 font-semibold">{r.disruption_id}</td>
                    <td className="py-2.5 px-3.5 font-sans">
                      <span className="text-neutral-800">{r.disruption_type}</span>
                    </td>
                    <td className="py-2.5 px-3.5 font-sans text-neutral-700">{r.industry}</td>
                    <td className="py-2.5 px-3 text-neutral-500 font-sans">T{r.supplier_tier}</td>
                    <td className="py-2.5 px-3.5 font-sans text-neutral-500">{r.supplier_region}</td>
                    <td className="py-2.5 px-3 text-center font-sans">
                      <span
                        className={`inline-block w-5 h-5 rounded-full text-center leading-5 text-[10px] font-semibold ${
                          r.disruption_severity >= 4
                            ? 'bg-red-50 text-red-700 border border-red-200'
                            : r.disruption_severity === 3
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        }`}
                      >
                        {r.disruption_severity}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-center font-sans">
                      {r.has_backup_supplier ? (
                        <span className="text-neutral-700 text-xs">
                          Yes
                        </span>
                      ) : (
                        <span className="text-neutral-400 text-xs">
                          No
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3.5 text-right font-mono text-neutral-800">
                      {Number(r.production_impact_pct).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-3.5 text-right font-mono text-neutral-800">
                      {formatCurrency(r.revenue_loss_usd)}
                    </td>
                    <td className="py-2.5 px-3 text-center font-mono text-neutral-500">
                      {r.full_recovery_days}d
                    </td>
                    <td className="py-2.5 px-3.5 text-center font-mono">
                      <span
                        className={
                          r.resilience_score < 50
                            ? 'text-red-700'
                            : 'text-neutral-800'
                        }
                      >
                        {Number(r.resilience_score).toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-2.5 px-3.5 text-center font-sans">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${getPriorityBadge(
                          r.prioritization_level
                        )}`}
                      >
                        {r.prioritization_level}
                      </span>
                    </td>
                    <td className="py-2.5 px-3.5 text-center font-sans">
                      <button
                        onClick={() => onSelectIncident && onSelectIncident(r)}
                        className="text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 border border-neutral-300 px-2.5 py-1 rounded text-xs font-medium transition-colors flex items-center space-x-1 mx-auto"
                        title="Load this incident into the 5-Agent Pipeline"
                      >
                        <span>Analyze</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 text-xs text-neutral-500">
        <div>
          Showing records{' '}
          <strong className="text-neutral-900 font-mono">
            {totalRecords === 0 ? 0 : (currentPage - 1) * pageSize + 1}
          </strong>{' '}
          to{' '}
          <strong className="text-neutral-900 font-mono">
            {Math.min(currentPage * pageSize, totalRecords)}
          </strong>{' '}
          of <strong className="text-neutral-900 font-mono">{totalRecords.toLocaleString()}</strong>
        </div>

        <div className="flex items-center space-x-1.5">
          {/* First Page */}
          <button
            onClick={() => handlePageChange(1)}
            disabled={currentPage === 1 || loading}
            className="p-1.5 rounded-md bg-neutral-50 border border-neutral-200 hover:bg-neutral-100 disabled:opacity-40 disabled:cursor-not-allowed text-neutral-700"
            title="First Page"
          >
            <ChevronsLeft className="w-4 h-4" />
          </button>

          {/* Previous Page */}
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1 || loading}
            className="flex items-center space-x-1 px-3 py-1.5 rounded-md bg-neutral-50 border border-neutral-200 hover:bg-neutral-100 disabled:opacity-40 disabled:cursor-not-allowed text-neutral-700"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Prev</span>
          </button>

          {/* Current Page Indicator */}
          <span className="px-3 py-1.5 bg-neutral-100 text-neutral-700 border border-neutral-200 rounded-md font-mono font-semibold">
            {currentPage}
          </span>

          {/* Next Page */}
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage >= totalPages || loading}
            className="flex items-center space-x-1 px-3 py-1.5 rounded-md bg-neutral-50 border border-neutral-200 hover:bg-neutral-100 disabled:opacity-40 disabled:cursor-not-allowed text-neutral-700"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>

          {/* Last Page */}
          <button
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage >= totalPages || loading}
            className="p-1.5 rounded-md bg-neutral-50 border border-neutral-200 hover:bg-neutral-100 disabled:opacity-40 disabled:cursor-not-allowed text-neutral-700"
            title="Last Page"
          >
            <ChevronsRight className="w-4 h-4" />
          </button>
        </div>
      </div>

    </div>
  );
}
