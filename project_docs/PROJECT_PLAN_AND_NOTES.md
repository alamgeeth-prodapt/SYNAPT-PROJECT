# Supply Chain Disruption Assistant (Project 9)
## Session Notes, Requirements & Implementation Plan
**Date:** October 8, 2026  
**Status:** Planning & Alignment Phase (Implementation paused awaiting user instruction)

---

## 1. Security & Operational Guidelines
- **Confidential Directory**: Do **not** access, read, or execute files in the `sql/` directory. It contains private AWS RDS credentials used for Synapt.
- **Credential Management**: All database and API keys will be managed purely via environment variables (`.env`), never hardcoded in scripts.
- **Dual Data Mode**: Support local storage (SQLite/Parquet) for offline development & testing, with dynamic environment variable support for AWS RDS / Synapt.

---

## 2. Requirements Summary (from Project 9 Specification)

### Context & Goal
Build a semantic retrieval and AI-assisted supply chain disruption analysis system using historical disruption records (100k events from `supply_chain_disruption_recovery.csv`).

### Requirement 1 – Basic Foundation
1. **Basic RAG System**: Semantic vector search for historical disruption cases.
2. **Hybrid Search**: Dense semantic retrieval + BM25 keyword matching.
3. **Disruption Classification Agent**: Auto-classification into standard disruption types (`Factory Incident`, `Cyber Attack`, `Port Congestion`, `Labor Strike`, `Geopolitical`, `Natural Disaster`).
4. **Metadata Filtering**: Filtering across `disruption_type`, `industry`, `supplier_tier` (1–4), `supplier_region`, and `disruption_severity` (1–5).
5. **Response & Recovery Recommendations**: Actionable mitigation strategies based on historical precedents.
6. **Input Validation Guardrails**: Schema checking, sanitization, and out-of-domain filter.
7. **Disruption Prioritization Engine**: Triage scoring combining severity, production impact %, and financial loss.
8. **API Endpoints**: FastAPI REST microservice.

### Requirement 2 – Advanced Capabilities
1. **DeepEval**: Quality evaluation harness (faithfulness, answer relevancy, context relevancy).
2. **Predictive ML Models**: Supervised models forecasting:
   - `production_impact_pct`
   - `revenue_loss_usd`
   - `full_recovery_days`
3. **LLM-as-Judge**: Validation agent checking recommendation quality, safety, and business feasibility.
4. **Multi-Agent Workflow**: Specialized pipeline:
   - *Investigation Agent* (retrieval & similar cases)
   - *Impact Assessment Agent* (ML predictions & resilience)
   - *Response Planning Agent* (mitigation actions)
   - *Recovery Analysis Agent* (recovery timelines & supplier change risk)
5. **Supply Chain Resilience & Risk Prediction**: Resilience index scoring based on supplier tiers, size, redundancy (`has_backup_supplier`).
6. **Explainable AI (XAI)**: SHAP feature importance & risk contribution factor analysis.
7. **Continuous Feedback Loop**: Capturing user feedback on recommendations to continuously improve benchmarks.
8. **Frontend Interface**: Interactive Streamlit web dashboard.

### Project Deliverables
- Architecture Diagram
- System Design Document
- Full Executable Code (Microservice + UI)
- 10-Minute Panel Presentation Outline

---

## 3. Step-by-Step Implementation Roadmap

```
Phase 1: Data Preparation & Preprocessing (Local 100k CSV cleaning & embedding text cards)
Phase 2: Hybrid RAG Engine (ChromaDB + BM25 + Reciprocal Rank Fusion + Metadata Filters)
Phase 3: Predictive ML Models & XAI (XGBoost regression for impact/revenue/recovery + SHAP)
Phase 4: Multi-Agent Workflow & LLM-as-Judge (Investigation, Impact, Planning, Recovery agents)
Phase 5: FastAPI Microservice & DeepEval Test Harness (REST API endpoints & automated evals)
Phase 6: Streamlit Frontend Dashboard & Presentation Deliverables
```

---
*Note: This session is permanently saved. No code or commands will be executed until explicitly requested.*
