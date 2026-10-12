import React, { useState } from 'react';
import {
  BookOpen,
  Layers,
  Cpu,
  BarChart3,
  Database,
  Lock,
  Terminal,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Shield,
  Activity,
  UserCheck,
  TrendingUp,
  FileText,
  Search,
  Zap,
  HelpCircle
} from 'lucide-react';

export default function InstructionsPage() {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: '1. System Overview', icon: BookOpen },
    { id: 'agents', label: '2. Multi-Agent Pipeline', icon: Layers },
    { id: 'ml', label: '3. Predictive ML & Chaining', icon: Cpu },
    { id: 'shap', label: '4. TreeSHAP Explainability', icon: BarChart3 },
    { id: 'synapt', label: '5. Synapt Trident MCP', icon: Database },
    { id: 'sql', label: '6. Natural Language SQL', icon: Search },
    { id: 'security', label: '7. Auth & Security', icon: Lock },
    { id: 'feedback', label: '8. Human-in-the-Loop', icon: UserCheck },
  ];

  return (
    <div className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full">
      
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-950 tracking-tight">
          Architecture & Operations Guide
        </h1>
        <p className="mt-2 text-xs sm:text-sm text-slate-500 max-w-3xl">
          Comprehensive reference for the 5-Agent crisis pipeline, XGBoost forecasting models, TreeSHAP explainability, and Synapt Trident MCP knowledge graph.
        </p>
      </div>

      {/* Main Grid: Sidebar Tabs + Content Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Navigation Sidebar */}
        <div className="lg:col-span-1 space-y-1.5">
          <div className="bg-white border border-slate-200/90 rounded-xl p-3 sticky top-24 shadow-sm">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-3 py-2">
              Feature Sections
            </p>
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs md:text-sm transition-all text-left ${
                    isActive
                      ? 'bg-slate-900 text-white font-semibold shadow-sm'
                      : 'text-slate-700 hover:text-slate-950 hover:bg-slate-100 font-medium'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Content Details Panel */}
        <div className="lg:col-span-3 space-y-8">
          
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6 md:p-8 space-y-6">
              <div className="border-b border-neutral-200 pb-4">
                <h2 className="text-2xl font-semibold text-neutral-900 flex items-center space-x-3">
                  <BookOpen className="w-6 h-6 text-neutral-700" />
                  <span>Platform Overview & Architecture</span>
                </h2>
                <p className="text-sm text-neutral-500 mt-1">
                  How the system solves modern supply chain volatility through empirical intelligence.
                </p>
              </div>

              <div className="prose prose-invert max-w-none text-neutral-700 text-sm leading-relaxed space-y-4">
                <p>
                  Global supply chains face frequent disruptions—including factory fires, ransomware cyberattacks,
                  port bottlenecks, strikes, and geopolitical crises. Operations teams traditionally struggle with
                  uncertainty regarding production downtime, dollar losses, and long recovery times.
                </p>
                <p>
                  This platform bridges that gap by unifying <b>5 cutting-edge technological pillars</b>:
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <span className="text-xs font-semibold text-neutral-700">Pillar 1</span>
                    <h4 className="font-semibold text-neutral-900 mt-1">100k MySQL Data Warehouse</h4>
                    <p className="text-xs text-neutral-500 mt-1">
                      Historical disruptions indexed in <code className="text-neutral-700">v_disruption_details</code> with real recovery outcomes.
                    </p>
                  </div>
                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <span className="text-xs font-semibold text-neutral-700">Pillar 2</span>
                    <h4 className="font-semibold text-neutral-900 mt-1">5 Autonomous Multi-Agents</h4>
                    <p className="text-xs text-neutral-500 mt-1">
                      Sequential investigation, impact, response, recovery, and LLM-as-Judge validation.
                    </p>
                  </div>
                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <span className="text-xs font-semibold text-neutral-700">Pillar 3</span>
                    <h4 className="font-semibold text-neutral-900 mt-1">Chained XGBoost ML Regressors</h4>
                    <p className="text-xs text-neutral-500 mt-1">
                      Downtime %, revenue loss $, and recovery day forecasting with chained causality.
                    </p>
                  </div>
                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <span className="text-xs font-semibold text-neutral-700">Pillar 4</span>
                    <h4 className="font-semibold text-neutral-900 mt-1">Synapt Trident MCP Knowledge Graph</h4>
                    <p className="text-xs text-neutral-500 mt-1">
                      Dynamic ontology governance across 33 controlled classes, preventing SQL hallucinations.
                    </p>
                  </div>
                </div>

                <div className="p-4 bg-neutral-100 border border-neutral-200 rounded-md text-neutral-700 text-xs flex items-start space-x-3">
                  <Zap className="w-5 h-5 shrink-0 mt-0.5 text-neutral-700" />
                  <div>
                    <span className="font-semibold">Sub-Second Execution:</span> The entire 5-agent pipeline,
                    including database queries, ML inference, and TreeSHAP waterfall calculation, executes
                    end-to-end in under 2 seconds.
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: MULTI-AGENT PIPELINE */}
          {activeTab === 'agents' && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6 md:p-8 space-y-6">
              <div className="border-b border-neutral-200 pb-4">
                <h2 className="text-2xl font-semibold text-neutral-900 flex items-center space-x-3">
                  <Layers className="w-6 h-6 text-neutral-700" />
                  <span>The 5 Autonomous Multi-Agents Explained</span>
                </h2>
                <p className="text-sm text-neutral-500 mt-1">
                  How each specialized agent performs its discrete operational duty.
                </p>
              </div>

              <div className="space-y-6 text-sm text-neutral-700">
                
                {/* Agent 1 */}
                <div className="p-5 bg-neutral-50 border border-neutral-200 rounded-md">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-neutral-100 text-neutral-700 border border-neutral-200">
                      Agent 1
                    </span>
                    <span className="text-xs text-neutral-500 font-mono">app/agents/investigation_agent.py</span>
                  </div>
                  <h3 className="text-base font-semibold text-neutral-900">Investigation Agent</h3>
                  <p className="mt-1 text-neutral-500 text-xs leading-relaxed">
                    <b>What it does:</b> Ingests the incident description and validates it against the Synapt Trident ontology.
                    Queries MySQL <code className="text-neutral-700">v_disruption_details</code> to retrieve the top 5 closest
                    historical disruption analogs and computes cohort baseline averages (mean impact %, mean loss $, mean recovery days).
                  </p>
                  <div className="mt-3 text-xs bg-white p-2.5 rounded-md border border-neutral-200 text-neutral-700">
                    <b>Output:</b> <code className="text-neutral-700">InvestigationResult</code> (analog cases, cohort statistics, historical baselines).
                  </div>
                </div>

                {/* Agent 2 */}
                <div className="p-5 bg-neutral-50 border border-neutral-200 rounded-md">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-neutral-100 text-neutral-700 border border-neutral-200">
                      Agent 2
                    </span>
                    <span className="text-xs text-neutral-500 font-mono">app/agents/impact_agent.py</span>
                  </div>
                  <h3 className="text-base font-semibold text-neutral-900">Impact Assessment Agent</h3>
                  <p className="mt-1 text-neutral-500 text-xs leading-relaxed">
                    <b>What it does:</b> Takes the 7 incident features and runs chained XGBoost inference. Computes the composite
                    <b>Resilience Score (0-100%)</b> and assigns triage priority (<code className="text-neutral-700">P1-Critical</code>, <code className="text-neutral-700">P2-High</code>, <code className="text-neutral-700">P3-Medium</code>, <code className="text-neutral-700">P4-Low</code>).
                    Invokes the SHAP service to isolate top positive risk drivers and negative mitigating offsets.
                  </p>
                  <div className="mt-3 text-xs bg-white p-2.5 rounded-md border border-neutral-200 text-neutral-700">
                    <b>Output:</b> <code className="text-neutral-700">ImpactResult</code> (predicted impact %, loss $, recovery days, Resilience Score, TreeSHAP drivers).
                  </div>
                </div>

                {/* Agent 3 */}
                <div className="p-5 bg-neutral-50 border border-neutral-200 rounded-md">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-neutral-100 text-neutral-700 border border-neutral-200">
                      Agent 3
                    </span>
                    <span className="text-xs text-neutral-500 font-mono">app/agents/response_agent.py</span>
                  </div>
                  <h3 className="text-base font-semibold text-neutral-900">Response Planning Agent</h3>
                  <p className="mt-1 text-neutral-500 text-xs leading-relaxed">
                    <b>What it does:</b> Benchmarks empirical mitigation outcomes in MySQL to determine which response
                    (Alternative Supplier, Production Reroute, Inventory Buffer, Expedited Freight) historically minimized revenue loss
                    and downtime for similar incidents. Generates an actionable operational checklist and execution SLA.
                  </p>
                  <div className="mt-3 text-xs bg-white p-2.5 rounded-md border border-neutral-200 text-neutral-700">
                    <b>Output:</b> <code className="text-neutral-700">ResponseResult</code> (optimal strategy, benchmark win rate, operational checklist, SLAs).
                  </div>
                </div>

                {/* Agent 4 */}
                <div className="p-5 bg-neutral-50 border border-neutral-200 rounded-md">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-neutral-100 text-neutral-700 border border-neutral-200">
                      Agent 4
                    </span>
                    <span className="text-xs text-neutral-500 font-mono">app/agents/recovery_agent.py</span>
                  </div>
                  <h3 className="text-base font-semibold text-neutral-900">Recovery Analysis Agent</h3>
                  <p className="mt-1 text-neutral-500 text-xs leading-relaxed">
                    <b>What it does:</b> Models the recovery resolution trajectory, projecting partial recovery days (50% throughput)
                    and full recovery days (100% capacity). Evaluates supplier contract continuity risk (Low to Severe) and synthesizes
                    a 4-phase milestone roadmap: (1) Containment, (2) Resource Substitution, (3) Capacity Ramp-up, (4) Post-Incident Governance.
                  </p>
                  <div className="mt-3 text-xs bg-white p-2.5 rounded-md border border-neutral-200 text-neutral-700">
                    <b>Output:</b> <code className="text-neutral-700">RecoveryResult</code> (4-phase milestone schedule, vendor continuity rating, ramp-up curve).
                  </div>
                </div>

                {/* Agent 5 */}
                <div className="p-5 bg-neutral-50 border border-neutral-200 rounded-md">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-neutral-100 text-neutral-700 border border-neutral-200">
                      Agent 5
                    </span>
                    <span className="text-xs text-neutral-500 font-mono">app/agents/judge.py</span>
                  </div>
                  <h3 className="text-base font-semibold text-neutral-900">LLM-as-Judge Validator</h3>
                  <p className="mt-1 text-neutral-500 text-xs leading-relaxed">
                    <b>What it does:</b> Acts as an automated governance auditor. Inspects the compiled response plan for critical
                    failure modes: single-source dependency risks (e.g., severe incidents with no backup supplier relying on alternative sourcing),
                    timeline feasibility violations, and budget realism. Emits a formal verdict: <code className="text-neutral-700">APPROVED</code> or <code className="text-neutral-700">FLAGGED_FOR_HUMAN_REVIEW</code>.
                  </p>
                  <div className="mt-3 text-xs bg-white p-2.5 rounded-md border border-neutral-200 text-neutral-700">
                    <b>Output:</b> <code className="text-neutral-700">JudgeVerdict</code> (verdict status, audit critique, safety score, risk checks).
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* TAB 3: PREDICTIVE ML & CHAINING */}
          {activeTab === 'ml' && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6 md:p-8 space-y-6">
              <div className="border-b border-neutral-200 pb-4">
                <h2 className="text-2xl font-semibold text-neutral-900 flex items-center space-x-3">
                  <Cpu className="w-6 h-6 text-neutral-700" />
                  <span>Predictive Machine Learning & Chained Inference</span>
                </h2>
                <p className="text-sm text-neutral-500 mt-1">
                  Input features, target outputs, model accuracy, and the chained causality design.
                </p>
              </div>

              <div className="space-y-6 text-sm text-neutral-700">
                <p>
                  The platform avoids generic LLM qualitative estimates by deploying three specialized XGBoost
                  regressors trained on 100,000 empirical historical records:
                </p>

                {/* Model Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  
                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <span className="text-xs font-semibold text-neutral-700">Model 1</span>
                    <h4 className="font-semibold text-neutral-900 mt-1">Production Impact %</h4>
                    <p className="text-xs text-neutral-500 mt-1">
                      Predicts plant downtime percentage (0.0% to 100.0%).
                    </p>
                    <div className="mt-3 pt-3 border-t border-neutral-200 text-xs">
                      <div><b>Inputs:</b> 7 Features</div>
                      <div className="text-neutral-700 mt-1"><b>R² = 0.70</b> | MAE = 7.82%</div>
                    </div>
                  </div>

                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md relative overflow-hidden">
                    <div className="absolute top-2 right-2 bg-neutral-100 text-neutral-700 text-[10px] px-1.5 py-0.5 rounded font-mono font-semibold">
                      CHAINED
                    </div>
                    <span className="text-xs font-semibold text-neutral-700">Model 2</span>
                    <h4 className="font-semibold text-neutral-900 mt-1">Revenue Loss USD</h4>
                    <p className="text-xs text-neutral-500 mt-1">
                      Predicts total financial loss ($ USD).
                    </p>
                    <div className="mt-3 pt-3 border-t border-neutral-200 text-xs">
                      <div><b>Inputs:</b> 7 Features + <b>Chained Impact %</b> (8 total)</div>
                      <div className="text-neutral-700 mt-1"><b>R² = 0.38</b> | MAE = $1.62M</div>
                    </div>
                  </div>

                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <span className="text-xs font-semibold text-neutral-700">Model 3</span>
                    <h4 className="font-semibold text-neutral-900 mt-1">Full Recovery Days</h4>
                    <p className="text-xs text-neutral-500 mt-1">
                      Predicts days until 100% operational throughput.
                    </p>
                    <div className="mt-3 pt-3 border-t border-neutral-200 text-xs">
                      <div><b>Inputs:</b> 7 Features</div>
                      <div className="text-neutral-700 mt-1"><b>R² = 0.55</b> | MAE = 26.27 days</div>
                    </div>
                  </div>

                </div>

                {/* Why Chaining Matters */}
                <div className="p-5 bg-neutral-100 border border-neutral-200 rounded-md">
                  <h4 className="font-semibold text-neutral-700 text-sm flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-neutral-700" />
                    <span>Why Chained Inference is Architecturally Critical</span>
                  </h4>
                  <p className="text-xs text-neutral-700 mt-2 leading-relaxed">
                    Financial revenue loss is physically caused by operational downtime. If Model 2 predicted loss
                    independently without knowing the output of Model 1, it could generate contradictory forecasts
                    (e.g., predicting $10M loss during a 2% minor disruption). By passing the predicted
                    <code className="text-neutral-700">production_impact_pct</code> as a dynamic input into Model 2,
                    the pipeline enforces <b>strict physical causality</b>.
                  </p>
                </div>

                {/* Resilience Formula */}
                <div className="p-5 bg-neutral-50 border border-neutral-200 rounded-md space-y-3">
                  <h4 className="font-semibold text-neutral-900 text-sm">Resilience Score Mathematical Formula</h4>
                  <p className="text-xs text-neutral-500">
                    Calculates a composite resilience index (0.0% to 100.0%) balancing downtime, dollar loss, duration, and supplier redundancy:
                  </p>
                  <pre className="bg-white p-3 rounded-md text-xs font-mono text-neutral-700 overflow-x-auto">
                    Resilience Score = 100 - [ 0.35 * Impact% + 0.25 * min(Loss/$100k, 100) + 0.20 * min(Days/2, 100) + 0.10 * (Severity*20) + 0.10 * RedundancyPenalty ]
                  </pre>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs pt-2">
                    <div className="bg-neutral-100 border border-neutral-200 p-2 rounded text-neutral-700">
                      <b>P1-Critical:</b> &lt; 50.0%
                    </div>
                    <div className="bg-neutral-100 border border-neutral-200 p-2 rounded text-neutral-700">
                      <b>P2-High:</b> 50.0% - 64.9%
                    </div>
                    <div className="bg-neutral-100 border border-neutral-200 p-2 rounded text-neutral-700">
                      <b>P3-Medium:</b> 65.0% - 79.9%
                    </div>
                    <div className="bg-neutral-100 border border-neutral-200 p-2 rounded text-neutral-700">
                      <b>P4-Low:</b> &ge; 80.0%
                    </div>
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* TAB 4: TREESHAP EXPLAINABILITY */}
          {activeTab === 'shap' && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6 md:p-8 space-y-6">
              <div className="border-b border-neutral-200 pb-4">
                <h2 className="text-2xl font-semibold text-neutral-900 flex items-center space-x-3">
                  <BarChart3 className="w-6 h-6 text-neutral-700" />
                  <span>TreeSHAP Local Explainability (XAI)</span>
                </h2>
                <p className="text-sm text-neutral-500 mt-1">
                  How to interpret waterfall plots and root-cause risk attributions.
                </p>
              </div>

              <div className="space-y-5 text-sm text-neutral-700 leading-relaxed">
                <p>
                  Instead of black-box predictions, the platform provides exact mathematical feature attributions
                  computed via native XGBoost C++ <code className="text-neutral-700">pred_contribs=True</code> in under 10 milliseconds.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <div className="flex items-center space-x-2 text-neutral-700 text-xs font-semibold mb-2">
                      <TrendingUp className="w-4 h-4" />
                      <span>Positive Risk Drivers (+)</span>
                    </div>
                    <p className="text-xs text-neutral-500">
                      Features that push predicted impact or financial loss <b>higher</b> than baseline.
                      For example: <i>Severity Level 4 (+14.2%)</i>, <i>No Backup Supplier (+11.8%)</i>, or <i>Tier 1 Supplier (+6.4%)</i>.
                    </p>
                  </div>

                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <div className="flex items-center space-x-2 text-neutral-700 text-xs font-semibold mb-2">
                      <Shield className="w-4 h-4" />
                      <span>Mitigating Offsets (-)</span>
                    </div>
                    <p className="text-xs text-neutral-500">
                      Features that buffer the organization and push impact <b>lower</b> than baseline.
                      For example: <i>Backup Supplier Active (-8.5%)</i>, <i>Large Supplier Size (-3.2%)</i>, or <i>Low Severity (-9.1%)</i>.
                    </p>
                  </div>
                </div>

                <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md space-y-2">
                  <h4 className="font-semibold text-neutral-900 text-xs">How to Read the Waterfall Plot:</h4>
                  <ol className="list-decimal list-inside space-y-1.5 text-xs text-neutral-700">
                    <li><b>Base Value E[f(x)]:</b> Represents the average historical expectation across all 100,000 cases.</li>
                    <li><b>Feature Contributions (&phi;):</b> Each bar represents the exact marginal impact of that specific attribute.</li>
                    <li><b>Final Output f(x):</b> The sum of the baseline plus all positive and negative feature contributions equals the exact predicted value.</li>
                  </ol>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: SYNAPT TRIDENT MCP */}
          {activeTab === 'synapt' && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6 md:p-8 space-y-6">
              <div className="border-b border-neutral-200 pb-4">
                <h2 className="text-2xl font-semibold text-neutral-900 flex items-center space-x-3">
                  <Database className="w-6 h-6 text-neutral-700" />
                  <span>Synapt Trident MCP Knowledge Graph</span>
                </h2>
                <p className="text-sm text-neutral-500 mt-1">
                  Semantic ontology governance and eliminating LLM SQL hallucinations.
                </p>
              </div>

              <div className="space-y-5 text-sm text-neutral-700 leading-relaxed">
                <p>
                  Standard LLMs frequently hallucinate non-existent database columns or query invalid category
                  strings (e.g., querying <code className="text-neutral-700">'Semiconductors'</code> when the database only recognizes
                  <code className="text-neutral-700">'Electronics'</code>).
                </p>
                <p>
                  <b>Synapt Trident MCP</b> provides a semantic knowledge graph ontology that acts as a ground-truth
                  governance barrier before SQL synthesis:
                </p>

                {/* 33 Controlled Classes Table */}
                <div className="border border-neutral-200 rounded-md overflow-hidden bg-neutral-50">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-white text-neutral-500 border-b border-neutral-200">
                      <tr>
                        <th className="p-3 font-semibold">Ontology Dimension</th>
                        <th className="p-3 font-semibold">Ground-Truth Classes (33 Total)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-100 text-neutral-700 font-mono">
                      <tr>
                        <td className="p-3 font-sans font-semibold text-neutral-500">Disruption Types (6)</td>
                        <td className="p-3 text-neutral-700">Factory Incident, Cyber Attack, Port Congestion, Labor Strike, Geopolitical, Natural Disaster</td>
                      </tr>
                      <tr>
                        <td className="p-3 font-sans font-semibold text-neutral-500">Industries (6)</td>
                        <td className="p-3 text-neutral-700">Electronics, Automotive, Pharmaceuticals, Consumer Goods, Aerospace, Energy</td>
                      </tr>
                      <tr>
                        <td className="p-3 font-sans font-semibold text-neutral-500">Supplier Tiers (4)</td>
                        <td className="p-3 text-neutral-700">Tier 1, Tier 2, Tier 3, Tier 4</td>
                      </tr>
                      <tr>
                        <td className="p-3 font-sans font-semibold text-neutral-500">Supplier Regions (6)</td>
                        <td className="p-3 text-neutral-700">Asia-Pacific, North America, Europe, Latin America, Middle East, Africa</td>
                      </tr>
                      <tr>
                        <td className="p-3 font-sans font-semibold text-neutral-500">Supplier Sizes (3)</td>
                        <td className="p-3 text-neutral-700">Small (&lt;250), Medium (250-1000), Large (&gt;1000)</td>
                      </tr>
                      <tr>
                        <td className="p-3 font-sans font-semibold text-neutral-500">Mitigation Strategies (8)</td>
                        <td className="p-3 text-neutral-700">Alternative Supplier, Production Reroute, Inventory Buffer, Expedited Freight, Supplier Financial Support, Emergency Protocols, Demand Shaping, Dual Sourcing</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div className="p-4 bg-neutral-100 border border-neutral-200 rounded-md text-neutral-700 text-xs flex items-start space-x-3">
                  <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5 text-neutral-700" />
                  <div>
                    <b>Entity Resolution in Action:</b> When a user asks for <i>"APAC chip shortages with no backup"</i>,
                    Synapt Trident automatically resolves <code className="text-neutral-900">"APAC" &rarr; "Asia-Pacific"</code>,
                    <code className="text-neutral-900">"chip" &rarr; "Electronics"</code>, and
                    <code className="text-neutral-900">"no backup" &rarr; has_backup_supplier = 0</code>.
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: NATURAL LANGUAGE SQL */}
          {activeTab === 'sql' && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6 md:p-8 space-y-6">
              <div className="border-b border-neutral-200 pb-4">
                <h2 className="text-2xl font-semibold text-neutral-900 flex items-center space-x-3">
                  <Search className="w-6 h-6 text-neutral-700" />
                  <span>Graph-Guided Natural Language SQL Console</span>
                </h2>
                <p className="text-sm text-neutral-500 mt-1">
                  How natural language queries are safely translated into read-only SQL.
                </p>
              </div>

              <div className="space-y-4 text-sm text-neutral-700 leading-relaxed">
                <p>
                  The SQL Builder service (<code className="text-neutral-700">app/services/sql_builder.py</code>) allows
                  operators to ask conversational questions about the 100,000 historical disruption records.
                </p>

                <h4 className="font-semibold text-neutral-900 text-xs">Example Queries You Can Try:</h4>
                <div className="space-y-2 text-xs">
                  <div className="bg-neutral-50 p-3 rounded-md border border-neutral-200 font-mono text-neutral-700">
                    "Show me factory fire disruptions in Automotive without backup supplier"
                  </div>
                  <div className="bg-neutral-50 p-3 rounded-md border border-neutral-200 font-mono text-neutral-700">
                    "Find severe cyber attacks affecting Tier 1 electronics suppliers in Asia-Pacific"
                  </div>
                  <div className="bg-neutral-50 p-3 rounded-md border border-neutral-200 font-mono text-neutral-700">
                    "List port congestion incidents where recovery took more than 60 days"
                  </div>
                </div>

                <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md space-y-2 text-xs">
                  <h4 className="font-semibold text-neutral-900">Strict Security Guardrails:</h4>
                  <ul className="list-disc list-inside space-y-1 text-neutral-500">
                    <li><b>Read-Only SELECT:</b> Blocks any mutating SQL commands (DROP, ALTER, UPDATE, DELETE, TRUNCATE).</li>
                    <li><b>AST Validation:</b> Rejects queries with unrecognized clauses or SQL injection patterns.</li>
                    <li><b>Automatic Scoping:</b> Automatically injects safe <code className="text-neutral-700">LIMIT 1 to 500</code> constraints.</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* TAB 7: AUTH & SECURITY */}
          {activeTab === 'security' && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6 md:p-8 space-y-6">
              <div className="border-b border-neutral-200 pb-4">
                <h2 className="text-2xl font-semibold text-neutral-900 flex items-center space-x-3">
                  <Lock className="w-6 h-6 text-neutral-700" />
                  <span>Authentication & Dual-Database Security Architecture</span>
                </h2>
                <p className="text-sm text-neutral-500 mt-1">
                  How credentials, sessions, and operational endpoints are protected.
                </p>
              </div>

              <div className="space-y-5 text-sm text-neutral-700 leading-relaxed">
                <p>
                  To adhere to enterprise information security standards, the platform uses <b>strict dual-database segregation</b>:
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <span className="text-xs font-semibold text-neutral-700">Isolated Auth Store</span>
                    <h4 className="font-semibold text-neutral-900 mt-1">SQLite (auth.db)</h4>
                    <p className="text-xs text-neutral-500 mt-1">
                      Stores user accounts, salted BCrypt password hashes, and RBAC roles. Completely isolated from MySQL.
                    </p>
                  </div>
                  <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md">
                    <span className="text-xs font-semibold text-neutral-700">Analytical Warehouse</span>
                    <h4 className="font-semibold text-neutral-900 mt-1">MySQL (supply_chain_db)</h4>
                    <p className="text-xs text-neutral-500 mt-1">
                      Contains 100,000 historical disruption records, normalized tables, and the unified view <code className="text-neutral-700">v_disruption_details</code>.
                    </p>
                  </div>
                </div>

                <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-md space-y-3 text-xs">
                  <h4 className="font-semibold text-neutral-900">Default Admin Credentials:</h4>
                  <div className="font-mono bg-white p-2.5 rounded border border-neutral-200 flex items-center justify-between">
                    <span>Username: <b>admin</b> | Password: <b>admin</b></span>
                    <span className="text-neutral-700">Pre-seeded</span>
                  </div>
                  <p className="text-neutral-500">
                    Mints PyJWT tokens signed with <code className="text-neutral-700">HS256</code> valid for 24 hours.
                    All operational endpoints (<code className="text-neutral-700">/orchestrate</code>, <code className="text-neutral-700">/predict</code>, <code className="text-neutral-700">/query-sql</code>)
                    require a valid <code className="text-neutral-700">Authorization: Bearer &lt;token&gt;</code> header.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 8: HUMAN-IN-THE-LOOP FEEDBACK */}
          {activeTab === 'feedback' && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6 md:p-8 space-y-6">
              <div className="border-b border-neutral-200 pb-4">
                <h2 className="text-2xl font-semibold text-neutral-900 flex items-center space-x-3">
                  <UserCheck className="w-6 h-6 text-neutral-700" />
                  <span>Human-in-the-Loop Governance & Feedback</span>
                </h2>
                <p className="text-sm text-neutral-500 mt-1">
                  How human operators audit AI decisions, provide ratings, and log governance records.
                </p>
              </div>

              <div className="space-y-4 text-sm text-neutral-700 leading-relaxed">
                <p>
                  AI decisions in mission-critical crisis scenarios require continuous human oversight.
                  The platform provides a dedicated feedback endpoint (<code className="text-neutral-700">POST /api/v1/feedback</code>)
                  allowing crisis directors to:
                </p>

                <div className="space-y-2 text-xs">
                  <div className="p-3 bg-neutral-50 border border-neutral-200 rounded-md flex items-start space-x-3">
                    <CheckCircle2 className="w-4 h-4 text-neutral-700 shrink-0 mt-0.5" />
                    <div>
                      <b>Rate Recommendation Quality (1 to 5 Stars):</b> Provides quantitative quality benchmarks
                      evaluating how closely the recommendation aligned with plant reality.
                    </div>
                  </div>
                  <div className="p-3 bg-neutral-50 border border-neutral-200 rounded-md flex items-start space-x-3">
                    <CheckCircle2 className="w-4 h-4 text-neutral-700 shrink-0 mt-0.5" />
                    <div>
                      <b>Accept or Override Response Strategy:</b> If an operator chooses a different mitigation path,
                      they record the rationale and override strategy for audit governance.
                    </div>
                  </div>
                  <div className="p-3 bg-neutral-50 border border-neutral-200 rounded-md flex items-start space-x-3">
                    <CheckCircle2 className="w-4 h-4 text-neutral-700 shrink-0 mt-0.5" />
                    <div>
                      <b>Permanent Audit Log:</b> Every feedback entry is stamped with the operator ID, dossier UUID,
                      and timestamp, ensuring a tamper-evident compliance paper trail.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
