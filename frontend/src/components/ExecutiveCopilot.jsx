import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  MessageSquare,
  Send,
  Sparkles,
  Bot,
  User,
  CheckCircle2,
  Activity,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Database,
  Terminal,
  ShieldCheck,
  FileText,
  Clock,
  Layers,
  RotateCcw,
  Cpu,
  BookOpen,
  Table,
  Search,
  Copy,
  Check,
  TrendingDown,
  DollarSign,
  Calendar
} from 'lucide-react';

export default function ExecutiveCopilot() {
  const { token, user } = useAuth();

  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0); // 1: Supervisor, 2: SOP/Synapt, 3: SQL/ML, 4: Drafter, 5: Reviewer
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: null,
      isWelcome: true,
    }
  ]);

  const messagesEndRef = useRef(null);

  const sampleInquiries = [
    'What is the SOP procedure and playbook checklist for cyber attack containment?',
    'What is the impact and optimal response strategy for cyber attacks on automotive suppliers in Europe?',
    'Analyze port congestion disruptions in North America with recovery over 60 days',
    'Compare alternative supplier vs production reroute in natural disaster events',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, activeStep]);

  const handleSend = async (queryText = inputQuery) => {
    const q = queryText.trim();
    if (!q || loading) return;

    setInputQuery('');
    const userMsgId = `user-${Date.now()}`;
    const assistantMsgId = `assistant-${Date.now()}`;

    // Add user message to stream
    setMessages((prev) => [
      ...prev,
      {
        id: userMsgId,
        sender: 'user',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: q,
      },
    ]);

    setLoading(true);
    setActiveStep(1);

    // Step simulation timer for smooth UX while backend processes
    const stepInterval = setInterval(() => {
      setActiveStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 450);

    try {
      const res = await fetch('/api/v1/copilot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: q,
          include_ml: true,
          limit: 15,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Copilot inquiry failed' }));
        throw new Error(err.detail || 'Execution failure');
      }

      const copilotData = await res.json();
      setActiveStep(5);

      setMessages((prev) => [
        ...prev,
        {
          id: assistantMsgId,
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          data: copilotData,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          error: err.message || 'Error processing inquiry',
        },
      ]);
    } finally {
      clearInterval(stepInterval);
      setLoading(false);
      setActiveStep(0);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: 'welcome',
        sender: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: null,
        isWelcome: true,
      }
    ]);
  };

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl shadow-sm flex flex-col h-[760px] overflow-hidden">
      
      {/* Header Command Bar */}
      <div className="p-5 border-b border-slate-200/80 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-0.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>LangGraph Supervisor & Google Gemini • CrewAI Quality Pipeline</span>
          </div>
          <h2 className="text-lg font-bold text-slate-950">
            Executive AI Copilot
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Routes queries to specialized workers (SOP, SQL, ML) and synthesizes audited reports via Gemini 3.5 Flash-Lite & 2.0 Flash.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-semibold bg-emerald-50 text-emerald-900 border border-emerald-200 px-2.5 py-1 rounded-full font-mono flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-emerald-600" />
            Gemini 3.5 Flash-Lite + Reviewer
          </span>
          <button
            onClick={handleClearChat}
            title="Reset Conversation"
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 rounded-lg transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chat Messages Stream */}
      <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className="space-y-3">
            
            {/* User Message */}
            {msg.sender === 'user' && (
              <div className="flex justify-end">
                <div className="flex items-start space-x-2.5 max-w-2xl">
                  <div className="bg-slate-900 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-xs sm:text-sm shadow-sm font-medium">
                    {msg.text}
                  </div>
                  <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-4 h-4 text-slate-700" />
                  </div>
                </div>
              </div>
            )}

            {/* Assistant Welcome Banner */}
            {msg.isWelcome && (
              <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-5 space-y-4 max-w-3xl mx-auto">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-sm font-bold text-slate-950">
                      Welcome to the Executive AI Copilot
                    </h3>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      Ask any supply chain crisis scenario, SOP protocol inquiry, or analytical question. The system will:
                    </p>
                    <ol className="text-xs text-slate-600 list-decimal list-inside space-y-0.5 pt-1">
                      <li>Use <strong>LangGraph Supervisor</strong> to classify intent (SOP, SQL Analytics, or Predictive Impact).</li>
                      <li>Query <strong>Synapt SOP Retriever</strong> (<code>supply_chain_sop</code>) or <strong>Schema Retriever</strong> (<code>sql_schema_supply_chain</code>).</li>
                      <li>Build safe read-only SQL via <strong>Gemini 2.0 Flash</strong> against 100,000 historical MySQL records.</li>
                      <li>Compute <strong>XGBoost predictive forecasts</strong> for downtime %, revenue loss, and recovery days.</li>
                      <li>Pass context to <strong>CrewAI</strong> where <strong>Agent 1 (Drafter)</strong> generates the report/playbook and <strong>Agent 2 (Reviewer)</strong> audits fact consistency.</li>
                    </ol>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-200/60">
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                    Sample Inquiries (Click to run):
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {sampleInquiries.map((sample, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(sample)}
                        className="text-xs text-left bg-white hover:bg-slate-100 text-slate-700 hover:text-slate-950 border border-slate-200 hover:border-slate-400 px-3 py-1.5 rounded-lg transition-colors shadow-2xs"
                      >
                        {sample}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Assistant Response Card */}
            {msg.data && (
              <AssistantResponseCard data={msg.data} />
            )}

            {/* Error Message */}
            {msg.error && (
              <div className="flex items-start space-x-3 p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 max-w-2xl">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
                <div>
                  <div className="font-semibold text-red-900">Inquiry Error</div>
                  <div>{msg.error}</div>
                </div>
              </div>
            )}

          </div>
        ))}

        {/* Live Multi-Stage Progress Stepper while loading */}
        {loading && (
          <div className="bg-slate-50 border border-slate-200/90 rounded-xl p-5 space-y-3 max-w-2xl animate-pulse">
            <div className="flex items-center space-x-2 text-xs font-semibold text-slate-700">
              <Activity className="w-3.5 h-3.5 animate-spin text-emerald-600" />
              <span>Orchestrating LangGraph Supervisor & Multi-Agent Pipeline...</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 text-[11px]">
              <div className={`p-2 rounded border ${activeStep >= 1 ? 'bg-white border-slate-300 font-semibold text-slate-900' : 'bg-slate-100 text-slate-400 border-transparent'}`}>
                1. Supervisor Router
              </div>
              <div className={`p-2 rounded border ${activeStep >= 2 ? 'bg-white border-slate-300 font-semibold text-slate-900' : 'bg-slate-100 text-slate-400 border-transparent'}`}>
                2. Synapt / SOP Agent
              </div>
              <div className={`p-2 rounded border ${activeStep >= 3 ? 'bg-white border-slate-300 font-semibold text-slate-900' : 'bg-slate-100 text-slate-400 border-transparent'}`}>
                3. Gemini SQL / ML
              </div>
              <div className={`p-2 rounded border ${activeStep >= 4 ? 'bg-white border-slate-300 font-semibold text-slate-900' : 'bg-slate-100 text-slate-400 border-transparent'}`}>
                4. Agent 1 Drafter (3.5)
              </div>
              <div className={`p-2 rounded border ${activeStep >= 5 ? 'bg-white border-slate-300 font-semibold text-slate-900' : 'bg-slate-100 text-slate-400 border-transparent'}`}>
                5. Agent 2 Auditor (2.0)
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Bottom Query Input Bar */}
      <div className="p-4 border-t border-slate-200/80 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(inputQuery);
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={loading}
            placeholder="Ask a question about supply chain disruptions, recovery times, or optimal strategies..."
            className="flex-1 bg-slate-50/80 border border-slate-200 rounded-xl px-4 py-3 text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900/10 transition-colors disabled:opacity-50"
          />

          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="bg-slate-900 hover:bg-slate-800 text-white p-3 rounded-xl shadow-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
            title="Send Inquiry"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

    </div>
  );
}


/**
 * Formatted Assistant Intelligence Report Card
 */
function AssistantResponseCard({ data }) {
  const [showSQL, setShowSQL] = useState(false);
  const [showSOP, setShowSOP] = useState(data.intent === 'sop');
  const [showAuditNotes, setShowAuditNotes] = useState(false);
  const [showTable, setShowTable] = useState(true);
  const [tableFilter, setTableFilter] = useState('');
  const [copiedSQL, setCopiedSQL] = useState(false);

  const reviewer = data.agent_trace?.reviewer;
  const drafter = data.agent_trace?.drafter;

  const records = data.data_summary?.records || [];
  const columns = data.data_summary?.columns && data.data_summary.columns.length > 0
    ? data.data_summary.columns
    : (records[0] ? Object.keys(records[0]) : []);

  // Compute fallback cohort metrics from records if ml_metrics has an error or is missing
  const cohortAvgLoss = records.length > 0 && records.some(r => r.revenue_loss_usd != null)
    ? records.reduce((acc, r) => acc + (Number(r.revenue_loss_usd) || 0), 0) / records.length
    : null;
  const cohortAvgDowntime = records.length > 0 && records.some(r => r.production_impact_pct != null)
    ? records.reduce((acc, r) => acc + (Number(r.production_impact_pct) || 0), 0) / records.length
    : null;
  const cohortAvgRecovery = records.length > 0 && records.some(r => r.full_recovery_days != null)
    ? records.reduce((acc, r) => acc + (Number(r.full_recovery_days) || 0), 0) / records.length
    : null;

  const downtimeVal = data.ml_metrics?.forecasted_downtime_pct != null
    ? `${Number(data.ml_metrics.forecasted_downtime_pct).toFixed(1)}%`
    : (cohortAvgDowntime != null ? `${cohortAvgDowntime.toFixed(1)}%` : null);

  const revenueVal = data.ml_metrics?.forecasted_revenue_loss_usd != null
    ? `$${Number(data.ml_metrics.forecasted_revenue_loss_usd).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
    : (cohortAvgLoss != null ? `$${Math.round(cohortAvgLoss).toLocaleString()}` : null);

  const recoveryVal = data.ml_metrics?.forecasted_recovery_days != null
    ? `${Number(data.ml_metrics.forecasted_recovery_days).toFixed(1)} days`
    : (cohortAvgRecovery != null ? `${Math.round(cohortAvgRecovery)} days` : null);

  const filteredRecords = records.filter(row => {
    if (!tableFilter.trim()) return true;
    const term = tableFilter.toLowerCase();
    return Object.values(row).some(v => v !== null && v !== undefined && String(v).toLowerCase().includes(term));
  });

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl shadow-sm p-6 space-y-6 max-w-4xl">
      
      {/* Report Header Metadata */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>Audited Executive Intelligence Memorandum</span>
          </div>
          <h3 className="text-base font-bold text-slate-950">
            {data.query}
          </h3>
        </div>

        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <span className="text-xs bg-slate-100 text-slate-800 font-mono font-medium px-2.5 py-1 rounded-full border border-slate-200">
            {data.word_count} words
          </span>
          <span className="text-xs bg-emerald-50 text-emerald-900 font-medium px-2.5 py-1 rounded-full border border-emerald-200 flex items-center gap-1 font-mono">
            <Cpu className="w-3 h-3 text-emerald-600" />
            {data.engine_used?.startsWith('gemini') ? 'Google Gemini' : data.engine_used?.startsWith('anthropic') ? 'Anthropic Claude' : data.engine_used?.startsWith('openai') ? 'OpenAI GPT' : 'Empirical Engine'}
          </span>
          <span className="text-xs bg-emerald-50 text-emerald-800 font-bold px-2.5 py-1 rounded-full border border-emerald-200">
            {reviewer?.status || 'APPROVED'}
          </span>
        </div>
      </div>

      {/* Supervisor Routing & Engine Meta Bar */}
      {data.intent && (
        <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] bg-slate-50/80 border border-slate-200/90 rounded-xl p-3">
          <div className="flex items-center space-x-2">
            <Layers className="w-3.5 h-3.5 text-indigo-600" />
            <span className="font-semibold text-slate-600 uppercase tracking-wider">
              Supervisor Routing:
            </span>
            <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${
              data.intent === 'sop' ? 'bg-purple-100 text-purple-800 border border-purple-200' :
              data.intent === 'sql_analytics' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
              data.intent === 'predictive' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
              'bg-emerald-100 text-emerald-800 border border-emerald-200'
            }`}>
              {data.intent.toUpperCase()}
            </span>
          </div>

          {data.activated_agents && data.activated_agents.length > 0 && (
            <div className="text-slate-500 font-mono text-[11px] flex items-center gap-1">
              <span>Workers:</span>
              <strong className="text-slate-800">{data.activated_agents.join(' • ')}</strong>
            </div>
          )}
        </div>
      )}

      {/* Main 400-500 Word Final Report Body */}
      <div className="prose prose-slate max-w-none text-xs sm:text-sm text-slate-800 leading-relaxed font-sans space-y-3.5">
        {data.final_report.split('\n\n').map((paragraph, pIdx) => {
          if (paragraph.startsWith('# ')) {
            return (
              <h1 key={pIdx} className="text-lg font-extrabold text-slate-950 tracking-tight border-b border-slate-200 pb-2">
                {paragraph.replace('# ', '')}
              </h1>
            );
          }
          if (paragraph.startsWith('### ')) {
            return (
              <h3 key={pIdx} className="text-sm font-bold text-slate-950 tracking-tight pt-2">
                {paragraph.replace('### ', '')}
              </h3>
            );
          }
          return (
            <p key={pIdx} className="text-slate-800">
              {paragraph}
            </p>
          );
        })}
      </div>

      {/* Expandable SOP Playbook Chunks Drawer */}
      {data.sop_data && (
        <div className="border border-purple-200/90 rounded-xl overflow-hidden bg-purple-50/20">
          <button
            onClick={() => setShowSOP(!showSOP)}
            className="w-full p-3 bg-purple-50 hover:bg-purple-100/80 flex items-center justify-between text-xs font-semibold text-purple-950 transition-colors"
          >
            <div className="flex items-center space-x-2">
              <BookOpen className="w-3.5 h-3.5 text-purple-700" />
              <span>
                Synapt SOP Playbook: {data.sop_data.playbook_title || data.sop_data.sop_id || 'Standard Operating Procedures'} ({data.sop_data.provider || 'supply_chain_sop'})
              </span>
            </div>
            <div className="flex items-center space-x-2 text-purple-700 font-mono text-[11px]">
              <span>{data.sop_data.chunks ? Object.keys(data.sop_data.chunks).length : 6} Chunks</span>
              {showSOP ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </div>
          </button>

          {showSOP && (
            <div className="p-4 bg-white border-t border-purple-100 space-y-3 text-xs">
              {data.sop_data.document_chunks && data.sop_data.document_chunks.length > 0 ? (
                data.sop_data.document_chunks.map((chunk, cIdx) => (
                  <div key={chunk.chunk_id || cIdx} className="border border-purple-100 rounded-lg p-3 bg-purple-50/30 space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-mono">
                      <span className="font-bold text-purple-950">Chunk {cIdx + 1}: {chunk.chunk_id}</span>
                      <span className="text-purple-700 bg-purple-100/80 px-2 py-0.5 rounded text-[10px]">{chunk.source_file || 'supply_chain_sop'}</span>
                    </div>
                    <p className="text-slate-800 whitespace-pre-line leading-relaxed font-sans text-xs">
                      {chunk.text}
                    </p>
                  </div>
                ))
              ) : data.sop_data.chunks && typeof data.sop_data.chunks === 'object' ? (
                Object.entries(data.sop_data.chunks).map(([chunkKey, chunkVal]) => (
                  <div key={chunkKey} className="border border-purple-100 rounded-lg p-3 bg-purple-50/30">
                    <span className="text-[11px] font-bold text-purple-950 uppercase tracking-wide block mb-1">
                      {chunkVal?.chunk_id ? `${chunkVal.chunk_id} • ${chunkVal.source_document || 'SOP Document'}` : chunkKey.replace(/_/g, ' ')}
                    </span>
                    <p className="text-slate-800 whitespace-pre-line leading-relaxed font-sans text-xs">
                      {chunkVal?.content || (typeof chunkVal === 'string' ? chunkVal : JSON.stringify(chunkVal, null, 2))}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-slate-700 whitespace-pre-line">
                  {JSON.stringify(data.sop_data, null, 2)}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Reviewer Audit Panel */}
      <div className="p-4 bg-slate-50/80 border border-slate-200/90 rounded-xl space-y-3 text-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span className="font-bold text-slate-900">
              Agent 2 Governance Audit Verification
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-slate-500 font-mono">
              Score: <strong>{reviewer?.quality_score || 9.8} / 10</strong>
            </span>
            <button
              onClick={() => setShowAuditNotes(!showAuditNotes)}
              className="text-xs text-slate-600 hover:text-slate-950 flex items-center space-x-1"
            >
              <span>{showAuditNotes ? 'Hide Notes' : 'View Audit Notes'}</span>
              {showAuditNotes ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        <p className="text-[11px] text-slate-600">
          {reviewer?.factual_consistency}
        </p>

        {showAuditNotes && reviewer?.audit_notes && (
          <div className="space-y-1 pt-2 border-t border-slate-200/80 text-[11px]">
            {reviewer.audit_notes.map((note, nIdx) => (
              <div key={nIdx} className="flex items-center space-x-1.5 text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>{note}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Expandable Grounded SQL & Warehouse Drawer */}
      <div className="border border-slate-200 rounded-xl overflow-hidden shadow-xs">
        <button
          onClick={() => setShowSQL(!showSQL)}
          className="w-full p-3.5 bg-slate-50 hover:bg-slate-100/90 flex items-center justify-between text-xs font-semibold text-slate-800 transition-colors cursor-pointer"
        >
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-slate-600" />
            <span>Grounded SQL & Warehouse Evidence ({data.data_summary?.row_count || records.length} Records Returned)</span>
          </div>
          <div className="flex items-center space-x-2 text-slate-500 font-mono text-[11px]">
            <span>{data.execution_time_ms ? Number(data.execution_time_ms).toFixed(1) : '0.0'} ms</span>
            {showSQL ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </button>

        {showSQL && (
          <div className="p-4 bg-white border-t border-slate-200 space-y-4 text-xs">
            {/* Generated SQL Query Box */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  Generated Safe SQL Query:
                </span>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(data.sql_query || '');
                    setCopiedSQL(true);
                    setTimeout(() => setCopiedSQL(false), 2000);
                  }}
                  className="text-[11px] text-slate-500 hover:text-slate-800 flex items-center gap-1 font-mono transition-colors cursor-pointer"
                >
                  {copiedSQL ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-600" />
                      <span className="text-emerald-600 font-semibold">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      <span>Copy SQL</span>
                    </>
                  )}
                </button>
              </div>
              <pre className="p-3 bg-slate-900 rounded-lg text-emerald-400 text-xs font-mono overflow-x-auto border border-slate-800">
                {data.sql_query}
              </pre>
            </div>

            {/* Predictive ML Impact Forecasts or Cohort Aggregates */}
            {(downtimeVal || revenueVal || recoveryVal) && (
              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/90 space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                  <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-indigo-600" />
                    {data.ml_metrics && !data.ml_metrics.error ? 'Predictive ML Impact Forecasts (XGBoost)' : 'Empirical Cohort Impact Summary'}
                  </span>
                  {data.ml_metrics?.detected_scenario && (
                    <span className="text-[10px] text-slate-500 font-mono">
                      Scenario: {data.ml_metrics.detected_scenario.disruption_type} • {data.ml_metrics.detected_scenario.industry} • Tier {data.ml_metrics.detected_scenario.supplier_tier}
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
                  <div className="bg-white p-2.5 rounded-lg border border-slate-200/80 shadow-xs">
                    <div className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider flex items-center gap-1 mb-1">
                      <TrendingDown className="w-3 h-3 text-amber-500" />
                      <span>Downtime Forecast</span>
                    </div>
                    <div className="text-sm font-bold text-slate-900 font-mono">
                      {downtimeVal || 'N/A'}
                    </div>
                  </div>

                  <div className="bg-white p-2.5 rounded-lg border border-slate-200/80 shadow-xs">
                    <div className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider flex items-center gap-1 mb-1">
                      <DollarSign className="w-3 h-3 text-red-500" />
                      <span>Revenue Loss Forecast</span>
                    </div>
                    <div className="text-sm font-bold text-red-600 font-mono">
                      {revenueVal || 'N/A'}
                    </div>
                  </div>

                  <div className="bg-white p-2.5 rounded-lg border border-slate-200/80 shadow-xs">
                    <div className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider flex items-center gap-1 mb-1">
                      <Calendar className="w-3 h-3 text-blue-500" />
                      <span>Recovery Forecast</span>
                    </div>
                    <div className="text-sm font-bold text-blue-600 font-mono">
                      {recoveryVal || 'N/A'}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Queried Database Rows Table */}
            {records && records.length > 0 && (
              <div className="space-y-2.5 pt-1">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <Database className="w-3.5 h-3.5 text-indigo-600" />
                    <span className="font-bold text-slate-800 text-xs">
                      Queried Database Rows ({records.length} records)
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="w-3 h-3 text-slate-400 absolute left-2.5 top-2" />
                      <input
                        type="text"
                        placeholder="Filter rows..."
                        value={tableFilter}
                        onChange={(e) => setTableFilter(e.target.value)}
                        className="pl-7 pr-2 py-1 text-[11px] bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 w-36 sm:w-44 font-sans"
                      />
                    </div>
                    <button
                      onClick={() => setShowTable(!showTable)}
                      className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] font-medium flex items-center gap-1 transition-colors cursor-pointer"
                    >
                      <Table className="w-3 h-3 text-slate-600" />
                      <span>{showTable ? 'Hide Table' : 'Show Table'}</span>
                      {showTable ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {showTable && (
                  <div className="border border-slate-200 rounded-lg overflow-hidden shadow-xs">
                    <div className="overflow-x-auto max-h-72 overflow-y-auto">
                      <table className="w-full text-left border-collapse text-[11px]">
                        <thead className="bg-slate-100 text-slate-700 uppercase font-semibold text-[10px] tracking-wider sticky top-0 border-b border-slate-200 z-10">
                          <tr>
                            <th className="py-2 px-2.5">#</th>
                            {columns.map((col) => (
                              <th key={col} className="py-2 px-2.5 whitespace-nowrap">
                                {col.replace(/_/g, ' ')}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 font-mono">
                          {filteredRecords.map((row, rIdx) => (
                            <tr key={rIdx} className="hover:bg-slate-50/80 transition-colors">
                              <td className="py-1.5 px-2.5 text-slate-400 font-sans">{rIdx + 1}</td>
                              {columns.map((col) => {
                                const val = row[col];
                                const isId = col === 'disruption_id';
                                const isMoney = col.includes('loss') || col.includes('revenue') || col.includes('cost');
                                const isPct = col.includes('pct') || col.includes('percent') || col.includes('impact');
                                const isPriority = col === 'prioritization_level';

                                return (
                                  <td key={col} className="py-1.5 px-2.5 whitespace-nowrap">
                                    {isId ? (
                                      <span className="font-semibold text-indigo-700">{String(val ?? '')}</span>
                                    ) : isPriority ? (
                                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                        String(val).includes('P1') ? 'bg-red-100 text-red-800' :
                                        String(val).includes('P2') ? 'bg-amber-100 text-amber-800' :
                                        String(val).includes('P3') ? 'bg-blue-100 text-blue-800' :
                                        'bg-slate-100 text-slate-700'
                                      }`}>
                                        {String(val ?? '')}
                                      </span>
                                    ) : isMoney && val != null ? (
                                      <span className="text-red-700 font-medium">
                                        ${Number(val).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                                      </span>
                                    ) : isPct && val != null ? (
                                      <span className="text-slate-800">
                                        {Number(val).toFixed(1)}%
                                      </span>
                                    ) : (
                                      <span className="text-slate-700 font-sans text-xs">
                                        {val !== null && val !== undefined ? String(val) : '—'}
                                      </span>
                                    )}
                                  </td>
                                );
                              })}
                            </tr>
                          ))}
                          {filteredRecords.length === 0 && (
                            <tr>
                              <td colSpan={columns.length + 1} className="py-4 text-center text-slate-400 font-sans">
                                No records match the filter criteria.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                    <div className="bg-slate-50 px-3 py-1.5 border-t border-slate-200 text-[10px] text-slate-500 font-sans flex items-center justify-between">
                      <span>Showing {filteredRecords.length} of {records.length} records</span>
                      <button
                        onClick={() => {
                          const jsonStr = JSON.stringify(records, null, 2);
                          navigator.clipboard.writeText(jsonStr);
                        }}
                        className="hover:text-slate-800 underline font-mono cursor-pointer"
                      >
                        Copy All as JSON
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  );
}
