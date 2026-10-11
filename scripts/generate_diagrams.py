"""
Generates high-resolution architecture diagrams for the Synapt Supply Chain PDF documentation.
Outputs:
1. docs/diagram_system_architecture.png
2. docs/diagram_multi_agent_pipeline.png
3. docs/diagram_ml_pipeline.png
4. docs/diagram_synapt_mcp_flow.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("D:/SYNAPT-PROJECT/docs", exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Master System Architecture Diagram
# -----------------------------------------------------------------------------
def create_master_architecture():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Background
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')

    # Title
    ax.text(7, 9.6, "AI-Powered Supply Chain Disruption Assistant with Synapt", 
            ha='center', va='center', color='#F8FAFC', fontsize=18, fontweight='bold')
    ax.text(7, 9.25, "Master System Architecture & Microservice Infrastructure", 
            ha='center', va='center', color='#94A3B8', fontsize=12)

    # Box styles
    def draw_box(x, y, w, h, bg_color, border_color, title, subtitle="", items=None):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12,rounding_size=0.15",
                                      facecolor=bg_color, edgecolor=border_color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.3, title, ha='center', va='center', color='#F8FAFC', 
                fontsize=11, fontweight='bold')
        if subtitle:
            ax.text(x + w/2, y + h - 0.6, subtitle, ha='center', va='center', color='#38BDF8', 
                    fontsize=9, fontstyle='italic')
        if items:
            start_y = y + h - (0.9 if subtitle else 0.65)
            for i, itm in enumerate(items):
                ax.text(x + 0.3, start_y - i*0.32, f"• {itm}", ha='left', va='center', 
                        color='#E2E8F0', fontsize=8.5)

    # 1. UI Layer
    draw_box(0.6, 7.2, 5.8, 1.6, '#1E293B', '#38BDF8', 
             "1. Client & User Interface Layer", "Modern Web Dashboard & Swagger UI",
             ["React + Tailwind CSS + Lucide + Recharts Dashboard", 
              "FastAPI Interactive Swagger UI (/docs) with OAuth2 Padlock",
              "Role-based Session Management & Real-time Visualizer"])

    # 2. Security & Auth Layer
    draw_box(7.6, 7.2, 5.8, 1.6, '#1E293B', '#F59E0B', 
             "2. Security & Authentication Layer", "Isolated SQLite DB (auth.db)",
             ["OAuth2 Password Bearer Flow (/api/v1/auth/login)", 
              "PyJWT (HS256) Token Minting & Profile Verification",
              "BCrypt Salted Password Hashing & Role Guardrails (admin/admin)"])

    # Arrow from Layer 1 & 2 down to Orchestrator
    ax.annotate("", xy=(7.0, 6.7), xytext=(7.0, 7.2),
                arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=2))

    # 3. Multi-Agent Orchestration Layer
    draw_box(0.6, 4.3, 12.8, 2.3, '#1E1B4B', '#818CF8', 
             "3. Multi-Agent Crisis Response Orchestration Engine", "5-Stage Agentic Pipeline",
             ["Investigation Agent: Schema ground-truthing, analog retrieval & cohort statistics on 100k cases",
              "Impact Assessment Agent: XGBoost inference (downtime %, financial loss $, recovery days) & P1-P4 triage",
              "Response Planning Agent: Empirical mitigation strategy benchmarking & operational checklist synthesis",
              "Recovery Analysis Agent: 4-stage operational milestone roadmap & vendor contract continuity scoring",
              "LLM-as-Judge Validator: Automated governance audit for safety, single-source risk, and feasibility"])

    # Arrows down to lower layers
    ax.annotate("", xy=(3.5, 3.8), xytext=(3.5, 4.3),
                arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=2))
    ax.annotate("", xy=(10.5, 3.8), xytext=(10.5, 4.3),
                arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=2))

    # 4. Predictive ML & TreeSHAP Layer
    draw_box(0.6, 1.4, 6.0, 2.4, '#1E293B', '#F43F5E', 
             "4. Predictive Machine Learning & XAI", "Multi-Target XGBoost & TreeSHAP",
             ["Model 1: Production Impact % (R²=0.70, MAE=7.82%)",
              "Model 2: Financial Revenue Loss USD (Chained input, MAE=$1.62M)",
              "Model 3: Days to Full Operational Recovery (R²=0.55)",
              "Resilience Scoring: Composite 0-100% Index & P1-P4 Triage",
              "TreeSHAP Attribution: Native C++ pred_contribs waterfall drivers"])

    # 5. Synapt Trident MCP & Semantic SQL Layer
    draw_box(7.4, 1.4, 6.0, 2.4, '#1E293B', '#34D399', 
             "5. Synapt Trident MCP & Safe SQL Engine", "Knowledge Graph & Semantic Grounding",
             ["Synapt Trident MCP Client: Async FastMCP JSON-RPC connector",
              "Ontology Governance: 33 controlled classes across 6 dimensions",
              "Entity Resolution: Maps user query text to controlled enums",
              "Safe SQL Synthesis: Prunes schema, blocks mutations, injects LIMIT",
              "Data Warehouse: MySQL supply_chain_db (100,000 disruption rows)"])

    # Bottom Metadata Bar
    rect_bot = patches.FancyBboxPatch((0.6, 0.3), 12.8, 0.7, boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor='#020617', edgecolor='#475569', linewidth=1.5)
    ax.add_patch(rect_bot)
    ax.text(7.0, 0.65, "Enterprise Production Architecture | Zero Secret Exposure | Dual-DB Isolation (Auth vs Analytical)",
            ha='center', va='center', color='#94A3B8', fontsize=9.5, fontweight='bold')

    plt.tight_layout()
    plt.savefig("D:/SYNAPT-PROJECT/docs/diagram_system_architecture.png", dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print("Created diagram_system_architecture.png")


# -----------------------------------------------------------------------------
# 2. Multi-Agent Crisis Response Pipeline Diagram
# -----------------------------------------------------------------------------
def create_multi_agent_pipeline():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')

    ax.text(7, 8.5, "Autonomous 5-Agent Crisis Response Pipeline", 
            ha='center', va='center', color='#F8FAFC', fontsize=17, fontweight='bold')
    ax.text(7, 8.15, "Sequential Orchestration & Governance Protocol in app/agents/coordinator.py", 
            ha='center', va='center', color='#94A3B8', fontsize=11)

    agents = [
        ("Step 1: Investigation Agent", "#38BDF8", 
         ["Schema grounding via Synapt MCP", 
          "Analog retrieval on 100k records", 
          "Cohort baseline statistics calculation"]),
        ("Step 2: Impact Assessment Agent", "#F43F5E", 
         ["Multi-model XGBoost inference", 
          "0-100% Resilience Index scoring", 
          "P1-P4 priority triage classification", 
          "TreeSHAP risk driver extraction"]),
        ("Step 3: Response Planning Agent", "#F59E0B", 
         ["Empirical historical strategy ranking", 
          "Strategic Playbook selection", 
          "Actionable operational checklist", 
          "Mitigation lead-time SLA synthesis"]),
        ("Step 4: Recovery Analysis Agent", "#34D399", 
         ["Full operational recovery forecast", 
          "Vendor contract continuity rating", 
          "4-Stage milestone roadmap generation", 
          "Post-crisis audit recommendations"]),
        ("Step 5: LLM-as-Judge Validator", "#A855F7", 
         ["Independent feasibility audit", 
          "Single-source dependency risk check", 
          "Recovery timeline consistency review", 
          "Verdict: APPROVED / FLAGGED"])
    ]

    # Draw agents as cards horizontally
    card_w = 2.4
    card_h = 4.4
    spacing = 0.28
    start_x = 0.5

    for i, (title, color, bullets) in enumerate(agents):
        x = start_x + i * (card_w + spacing)
        y = 2.8
        rect = patches.FancyBboxPatch((x, y), card_w, card_h, boxstyle="round,pad=0.1,rounding_size=0.12",
                                      facecolor='#1E293B', edgecolor=color, linewidth=2)
        ax.add_patch(rect)

        # Header box
        hdr = patches.FancyBboxPatch((x, y + card_h - 0.9), card_w, 0.9, boxstyle="round,pad=0.08,rounding_size=0.1",
                                     facecolor=color, edgecolor=color, linewidth=1)
        ax.add_patch(hdr)
        ax.text(x + card_w/2, y + card_h - 0.45, title.split(":")[0], ha='center', va='center', 
                color='#0F172A', fontsize=10, fontweight='bold')
        ax.text(x + card_w/2, y + card_h - 0.72, title.split(":")[1].strip(), ha='center', va='center', 
                color='#0F172A', fontsize=8.5, fontweight='bold')

        # Bullets
        for b_idx, bullet in enumerate(bullets):
            ax.text(x + 0.15, y + card_h - 1.25 - b_idx*0.7, f"• {bullet}", 
                    ha='left', va='top', color='#F1F5F9', fontsize=8, wrap=True)

        # Connector arrow to next agent
        if i < len(agents) - 1:
            arr_x = x + card_w + 0.05
            ax.annotate("", xy=(arr_x + spacing - 0.1, y + card_h/2), xytext=(arr_x, y + card_h/2),
                        arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=2.5))

    # Input Box at Bottom Left
    rect_inp = patches.FancyBboxPatch((0.8, 0.7), 4.2, 1.4, boxstyle="round,pad=0.1,rounding_size=0.1",
                                      facecolor='#020617', edgecolor='#38BDF8', linewidth=1.5)
    ax.add_patch(rect_inp)
    ax.text(2.9, 1.7, "INPUT: IncidentInput Guardrail", ha='center', va='center', color='#38BDF8', 
            fontsize=9.5, fontweight='bold')
    ax.text(2.9, 1.2, "Disruption Type, Industry, Supplier Tier, Region,\nSupplier Size, Backup Redundancy, Severity (1-5)", 
            ha='center', va='center', color='#CBD5E1', fontsize=8)

    # Output Box at Bottom Right
    rect_out = patches.FancyBboxPatch((8.8, 0.7), 4.4, 1.4, boxstyle="round,pad=0.1,rounding_size=0.1",
                                      facecolor='#020617', edgecolor='#A855F7', linewidth=1.5)
    ax.add_patch(rect_out)
    ax.text(11.0, 1.7, "OUTPUT: ExecutiveDossier", ha='center', va='center', color='#A855F7', 
            fontsize=9.5, fontweight='bold')
    ax.text(11.0, 1.2, "Dossier ID, Timestamp, Triage Level, Risk Drivers,\nMitigation Plan, Milestones & Audit Verdict", 
            ha='center', va='center', color='#CBD5E1', fontsize=8)

    # Arrows from input and to output
    ax.annotate("", xy=(1.7, 2.7), xytext=(2.9, 2.1),
                arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=2))
    ax.annotate("", xy=(11.0, 2.1), xytext=(12.0, 2.7),
                arrowprops=dict(arrowstyle="->", color="#A855F7", lw=2))

    plt.tight_layout()
    plt.savefig("D:/SYNAPT-PROJECT/docs/diagram_multi_agent_pipeline.png", dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print("Created diagram_multi_agent_pipeline.png")


# -----------------------------------------------------------------------------
# 3. Machine Learning Architecture & Chained Inference Diagram
# -----------------------------------------------------------------------------
def create_ml_pipeline():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')

    ax.text(7, 8.5, "Predictive Machine Learning Engine & TreeSHAP Attribution", 
            ha='center', va='center', color='#F8FAFC', fontsize=17, fontweight='bold')
    ax.text(7, 8.15, "Chained XGBoost Regressors, Resilience Index Scoring, and Explainable AI", 
            ha='center', va='center', color='#94A3B8', fontsize=11)

    # Features input box
    rect_feat = patches.FancyBboxPatch((0.6, 2.2), 3.2, 5.0, boxstyle="round,pad=0.1,rounding_size=0.12",
                                       facecolor='#1E293B', edgecolor='#38BDF8', linewidth=2)
    ax.add_patch(rect_feat)
    ax.text(2.2, 6.8, "Raw Feature Inputs", ha='center', va='center', color='#38BDF8', 
            fontsize=11, fontweight='bold')
    ax.text(2.2, 6.45, "(7 Incident Attributes)", ha='center', va='center', color='#94A3B8', fontsize=8.5)
    
    features = [
        "1. disruption_type (Categorical)",
        "2. industry (Categorical)",
        "3. supplier_tier (Int 1-4)",
        "4. supplier_region (Categorical)",
        "5. supplier_size (Categorical)",
        "6. has_backup_supplier (0 or 1)",
        "7. disruption_severity (Int 1-5)"
    ]
    for idx, f in enumerate(features):
        ax.text(0.85, 5.9 - idx*0.5, f, ha='left', va='center', color='#F1F5F9', fontsize=8.5)

    # Model 1
    m1 = patches.FancyBboxPatch((4.7, 5.2), 4.3, 1.9, boxstyle="round,pad=0.1,rounding_size=0.12",
                                facecolor='#1E293B', edgecolor='#F43F5E', linewidth=2)
    ax.add_patch(m1)
    ax.text(6.85, 6.75, "Model 1: Production Impact %", ha='center', va='center', color='#F43F5E', 
            fontsize=10.5, fontweight='bold')
    ax.text(6.85, 6.4, "XGBoost Regressor (production_impact_model.json)", ha='center', va='center', color='#FDA4AF', fontsize=8)
    ax.text(4.9, 6.0, "• Inputs: 7 Features", color='#CBD5E1', fontsize=8)
    ax.text(4.9, 5.7, "• Output: production_impact_pct (0.0% - 100.0%)", color='#CBD5E1', fontsize=8)
    ax.text(4.9, 5.4, "• Accuracy: R² = 0.70 | MAE = 7.82%", color='#34D399', fontsize=8, fontweight='bold')

    # Model 2 (Chained!)
    m2 = patches.FancyBboxPatch((4.7, 2.6), 4.3, 2.1, boxstyle="round,pad=0.1,rounding_size=0.12",
                                facecolor='#1E293B', edgecolor='#F59E0B', linewidth=2)
    ax.add_patch(m2)
    ax.text(6.85, 4.35, "Model 2: Financial Loss USD (Chained)", ha='center', va='center', color='#F59E0B', 
            fontsize=10.5, fontweight='bold')
    ax.text(6.85, 4.05, "XGBoost Regressor (revenue_loss_model.json)", ha='center', va='center', color='#FDE68A', fontsize=8)
    ax.text(4.9, 3.65, "• Inputs: 7 Features + Chained Impact % (8 total!)", color='#CBD5E1', fontsize=8)
    ax.text(4.9, 3.35, "• Output: revenue_loss_usd ($ Continuous Loss)", color='#CBD5E1', fontsize=8)
    ax.text(4.9, 3.05, "• Accuracy: R² = 0.38 | MAE = $1.62M", color='#34D399', fontsize=8, fontweight='bold')
    ax.text(4.9, 2.75, "★ Chaining prevents unrealistic financial forecasts", color='#38BDF8', fontsize=7.5, fontstyle='italic')

    # Model 3
    m3 = patches.FancyBboxPatch((4.7, 0.4), 4.3, 1.8, boxstyle="round,pad=0.1,rounding_size=0.12",
                                facecolor='#1E293B', edgecolor='#A855F7', linewidth=2)
    ax.add_patch(m3)
    ax.text(6.85, 1.85, "Model 3: Full Recovery Days", ha='center', va='center', color='#A855F7', 
            fontsize=10.5, fontweight='bold')
    ax.text(6.85, 1.55, "XGBoost Regressor (full_recovery_days_model.json)", ha='center', va='center', color='#E9D5FF', fontsize=8)
    ax.text(4.9, 1.2, "• Inputs: 7 Features", color='#CBD5E1', fontsize=8)
    ax.text(4.9, 0.9, "• Output: full_recovery_days (Operational Duration)", color='#CBD5E1', fontsize=8)
    ax.text(4.9, 0.6, "• Accuracy: R² = 0.55 | MAE = 26.27 days", color='#34D399', fontsize=8, fontweight='bold')

    # Arrows from Features to Models
    ax.annotate("", xy=(4.6, 6.1), xytext=(3.8, 5.5),
                arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=1.8))
    ax.annotate("", xy=(4.6, 3.8), xytext=(3.8, 4.5),
                arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=1.8))
    ax.annotate("", xy=(4.6, 1.3), xytext=(3.8, 3.5),
                arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=1.8))

    # Chaining Arrow from M1 down into M2
    ax.annotate("", xy=(6.85, 4.7), xytext=(6.85, 5.2),
                arrowprops=dict(arrowstyle="->", color="#F43F5E", lw=2.5, ls="--"))
    ax.text(7.2, 4.95, "Chained\nImpact %", color='#FDA4AF', fontsize=7.5, fontweight='bold')

    # Right Column: Resilience & SHAP Box
    res_box = patches.FancyBboxPatch((9.7, 4.1), 3.7, 3.1, boxstyle="round,pad=0.1,rounding_size=0.12",
                                     facecolor='#1E293B', edgecolor='#34D399', linewidth=2)
    ax.add_patch(res_box)
    ax.text(11.55, 6.85, "Resilience Score & Triage", ha='center', va='center', color='#34D399', 
            fontsize=10.5, fontweight='bold')
    ax.text(11.55, 6.5, "Multi-Factor Mathematical Formula", ha='center', va='center', color='#A7F3D0', fontsize=8)
    ax.text(9.9, 6.0, "• Range: 0.0% (Fragile) to 100.0% (Resilient)", color='#F1F5F9', fontsize=8)
    ax.text(9.9, 5.65, "• Weights: Impact 35%, Loss 25%, Days 20%", color='#CBD5E1', fontsize=7.5)
    ax.text(9.9, 5.35, "• Penalties: Severity 10%, No-Backup 10%", color='#CBD5E1', fontsize=7.5)
    ax.text(9.9, 4.95, "Triage Classification:", color='#F8FAFC', fontsize=8, fontweight='bold')
    ax.text(9.9, 4.65, "• P1-Critical (< 50%)  |  P2-High (50-65%)", color='#FDA4AF', fontsize=7.5)
    ax.text(9.9, 4.35, "• P3-Medium (65-80%)  |  P4-Low (≥ 80%)", color='#BAE6FD', fontsize=7.5)

    shap_box = patches.FancyBboxPatch((9.7, 0.4), 3.7, 3.2, boxstyle="round,pad=0.1,rounding_size=0.12",
                                      facecolor='#1E293B', edgecolor='#818CF8', linewidth=2)
    ax.add_patch(shap_box)
    ax.text(11.55, 3.25, "TreeSHAP Explainability", ha='center', va='center', color='#818CF8', 
            fontsize=10.5, fontweight='bold')
    ax.text(11.55, 2.9, "Native C++ pred_contribs=True", ha='center', va='center', color='#C7D2FE', fontsize=8)
    ax.text(9.9, 2.45, "• Fast local feature attribution (<10ms)", color='#F1F5F9', fontsize=8)
    ax.text(9.9, 2.1, "• Computes baseline expected value E[f(x)]", color='#CBD5E1', fontsize=7.5)
    ax.text(9.9, 1.75, "• Identifies Top Positive Risk Drivers (+)", color='#F87171', fontsize=7.5)
    ax.text(9.9, 1.4, "• Identifies Mitigating Offsets (-)", color='#4ADE80', fontsize=7.5)
    ax.text(9.9, 0.95, "• Emits JSON for Waterfall UI Charts", color='#38BDF8', fontsize=7.5, fontweight='bold')

    # Arrows to right column
    ax.annotate("", xy=(9.6, 5.6), xytext=(9.0, 5.6),
                arrowprops=dict(arrowstyle="->", color="#34D399", lw=2))
    ax.annotate("", xy=(9.6, 2.0), xytext=(9.0, 3.2),
                arrowprops=dict(arrowstyle="->", color="#818CF8", lw=2))

    plt.tight_layout()
    plt.savefig("D:/SYNAPT-PROJECT/docs/diagram_ml_pipeline.png", dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print("Created diagram_ml_pipeline.png")


# -----------------------------------------------------------------------------
# 4. Synapt Trident MCP & Safe SQL Engine Diagram
# -----------------------------------------------------------------------------
def create_synapt_mcp_flow():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')

    ax.text(7, 8.5, "Synapt Trident MCP Knowledge Graph & SQL Synthesis Flow", 
            ha='center', va='center', color='#F8FAFC', fontsize=17, fontweight='bold')
    ax.text(7, 8.15, "Ontology Governance, Semantic Grounding, and Safe Read-Only SQL Generation", 
            ha='center', va='center', color='#94A3B8', fontsize=11)

    steps = [
        ("1. User NL Query", "#38BDF8", 
         ["Natural language prompt:", 
          "'Find severe factory fire", 
          "disruptions in Automotive", 
          "without backup supplier'"]),
        ("2. Column Pruner", "#818CF8", 
         ["Keyword & intent analysis", 
          "Prunes 15 view columns to:", 
          "• disruption_type", 
          "• industry", 
          "• has_backup_supplier", 
          "• disruption_severity"]),
        ("3. Synapt MCP Grounding", "#34D399", 
         ["Queries Synapt Knowledge Graph:", 
          "• 33 controlled classes", 
          "• Entity resolution mappings", 
          "• 'factory fire' -> 'Factory Incident'", 
          "• 'without backup' -> 0"]),
        ("4. Safe SQL Builder", "#F59E0B", 
         ["Synthesizes strict SQL:", 
          "SELECT disruption_id, ...", 
          "FROM v_disruption_details", 
          "WHERE disruption_type = '...'", 
          "AND has_backup = 0 LIMIT 50"]),
        ("5. Guardrail Execution", "#10B981", 
         ["Security & Execution:", 
          "• Blocks DROP/ALTER/UPDATE", 
          "• Enforces SELECT-only", 
          "• Runs on MySQL (100k rows)", 
          "• Returns JSON in <150ms"])
    ]

    card_w = 2.4
    card_h = 4.4
    spacing = 0.28
    start_x = 0.5

    for i, (title, color, bullets) in enumerate(steps):
        x = start_x + i * (card_w + spacing)
        y = 2.8
        rect = patches.FancyBboxPatch((x, y), card_w, card_h, boxstyle="round,pad=0.1,rounding_size=0.12",
                                      facecolor='#1E293B', edgecolor=color, linewidth=2)
        ax.add_patch(rect)

        hdr = patches.FancyBboxPatch((x, y + card_h - 0.9), card_w, 0.9, boxstyle="round,pad=0.08,rounding_size=0.1",
                                     facecolor=color, edgecolor=color, linewidth=1)
        ax.add_patch(hdr)
        parts = title.split(".", 1) if "." in title else title.split(":", 1)
        ax.text(x + card_w/2, y + card_h - 0.45, parts[0].strip(), ha='center', va='center', 
                color='#0F172A', fontsize=10, fontweight='bold')
        sub_title = parts[1].strip() if len(parts) > 1 else ""
        ax.text(x + card_w/2, y + card_h - 0.72, sub_title, ha='center', va='center', 
                color='#0F172A', fontsize=8.5, fontweight='bold')

        for b_idx, bullet in enumerate(bullets):
            ax.text(x + 0.15, y + card_h - 1.25 - b_idx*0.65, bullet, 
                    ha='left', va='top', color='#F1F5F9', fontsize=8)

        if i < len(steps) - 1:
            arr_x = x + card_w + 0.05
            ax.annotate("", xy=(arr_x + spacing - 0.1, y + card_h/2), xytext=(arr_x, y + card_h/2),
                        arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=2.5))

    # Bottom Callout: Why Synapt Matters
    callout = patches.FancyBboxPatch((0.5, 0.6), 13.0, 1.6, boxstyle="round,pad=0.1,rounding_size=0.12",
                                     facecolor='#020617', edgecolor='#34D399', linewidth=1.8)
    ax.add_patch(callout)
    ax.text(7.0, 1.85, "Why Synapt Trident MCP is Indispensable for Enterprise Supply Chain AI", 
            ha='center', va='center', color='#34D399', fontsize=10.5, fontweight='bold')
    
    reasons = [
        "1. Hallucination Prevention: Eliminates fabricated columns and invalid categorical values before SQL generation.",
        "2. Semantic Vocabulary Grounding: Translates ambiguous business terminology into exact database categorical codes.",
        "3. Zero SQL Injection Risk: Schema constraints and parameter binding prevent data exfiltration and mutations.",
        "4. High Availability Caching: In-memory TTL cache with graceful offline fallback ensures 100% service uptime."
    ]
    for r_idx, r in enumerate(reasons):
        ax.text(0.8, 1.45 - r_idx*0.28, r, ha='left', va='center', color='#CBD5E1', fontsize=8)

    plt.tight_layout()
    plt.savefig("D:/SYNAPT-PROJECT/docs/diagram_synapt_mcp_flow.png", dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print("Created diagram_synapt_mcp_flow.png")


if __name__ == "__main__":
    create_master_architecture()
    create_multi_agent_pipeline()
    create_ml_pipeline()
    create_synapt_mcp_flow()
    print("All 4 architecture diagrams generated successfully!")
