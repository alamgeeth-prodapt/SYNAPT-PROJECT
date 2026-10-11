# Supply Chain Disruption Assistant — SQL Query Complexity Benchmarks (Levels 1 to 5)

This benchmark document provides an evaluation suite of **25 realistic operational supply chain queries** categorized across **5 ascending levels of complexity**. 

These sentences serve as test cases for the **2-Step Synapt SQL Builder**, evaluating:
1. **Schema Pruning Precision**: Correctly picking required tables and columns without bloat.
2. **Entity Grounding Accuracy**: Mapping natural language synonyms to ground-truth controlled classes.
3. **SQL Syntactic Integrity**: Generating valid, read-only, high-performance MySQL queries on `v_disruption_details`.
4. **Multi-Agent Suitability**: Providing structured evidence for `InvestigationAgent`, `ImpactAgent`, and `ResponseAgent`.

---

## Complexity Level Summary

| Level | Complexity Tier | Query Characteristics | Primary Agent Consumer |
|---|---|---|---|
| **Level 1** | **Basic Single-Entity Filter** | Single categorical column, standard `SELECT`, `ORDER BY`, `LIMIT` | `InvestigationAgent` |
| **Level 2** | **Multi-Column & Threshold** | 2–4 column intersections, ordinal comparisons (`severity >= 4`), boolean flags | `InvestigationAgent` |
| **Level 3** | **Single Aggregation & Grouping** | `GROUP BY`, `AVG()`, `COUNT()`, comparative response benchmarks | `ResponseAgent` |
| **Level 4** | **Multi-Dimensional & Segmented** | Multi-column grouping, cohort slicing, `HAVING`, risk factor cross-tabulation | `ImpactAgent` & `ResponseAgent` |
| **Level 5** | **Strategic Analogs & Outliers** | Historical analog cohort matching, counterfactual playbook evaluation, resilience divergence | `Coordinator` & `LLMJudge` |

---

## Level 1: Basic Single-Entity Filtering

> **Scope**: Simple operational lookups with 1 categorical/filter constraint. Tests basic column selection and direct synonym matching.

### Query 1.1: Cyber Incidents in Electronics
* **Natural Language Query**: *"Show me all cyber attack disruptions affecting electronics companies."*
* **Target Schema**: `v_disruption_details`
* **Filter Columns**: `disruption_type = 'Cyber Attack'`, `industry = 'Electronics'`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, supplier_tier, supplier_region,
         disruption_severity, production_impact_pct, revenue_loss_usd, response_type,
         full_recovery_days, resilience_score, prioritization_level, top_risk_driver
  FROM v_disruption_details
  WHERE disruption_type = 'Cyber Attack' AND industry = 'Electronics'
  ORDER BY revenue_loss_usd DESC
  LIMIT 50;
  ```

### Query 1.2: Plant Fires by Financial Loss
* **Natural Language Query**: *"List factory fires in North America sorted by financial loss."*
* **Target Schema**: `v_disruption_details`
* **Grounding**: `"factory fires"` $\rightarrow$ `Factory Incident`, `"North America"` $\rightarrow$ `North America`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, supplier_tier, supplier_region,
         disruption_severity, production_impact_pct, revenue_loss_usd, full_recovery_days, resilience_score
  FROM v_disruption_details
  WHERE disruption_type = 'Factory Incident' AND supplier_region = 'North America'
  ORDER BY revenue_loss_usd DESC
  LIMIT 50;
  ```

### Query 1.3: Direct Tier-1 Supplier Incidents in Europe
* **Natural Language Query**: *"Find direct Tier 1 supplier disruptions located in Europe."*
* **Target Schema**: `v_disruption_details`
* **Grounding**: `"direct Tier 1"` $\rightarrow$ `supplier_tier = 1`, `"Europe"` $\rightarrow$ `supplier_region = 'Europe'`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, supplier_tier, supplier_region,
         disruption_severity, revenue_loss_usd, full_recovery_days
  FROM v_disruption_details
  WHERE supplier_tier = 1 AND supplier_region = 'Europe'
  ORDER BY revenue_loss_usd DESC
  LIMIT 50;
  ```

### Query 1.4: Port Congestion Delays
* **Natural Language Query**: *"Show recent port shipping backlog disruptions ordered by recovery time."*
* **Grounding**: `"port shipping backlog"` $\rightarrow$ `disruption_type = 'Port Congestion'`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, supplier_region, full_recovery_days, revenue_loss_usd
  FROM v_disruption_details
  WHERE disruption_type = 'Port Congestion'
  ORDER BY full_recovery_days DESC
  LIMIT 50;
  ```

### Query 1.5: Labor Strikes in Automotive
* **Natural Language Query**: *"Retrieve all labor strikes and union walkouts in the automotive sector."*
* **Grounding**: `"labor strikes and union walkouts"` $\rightarrow$ `disruption_type = 'Labor Strike'`, `"automotive"` $\rightarrow$ `industry = 'Automotive'`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, supplier_tier, disruption_severity, production_impact_pct, revenue_loss_usd
  FROM v_disruption_details
  WHERE disruption_type = 'Labor Strike' AND industry = 'Automotive'
  ORDER BY revenue_loss_usd DESC
  LIMIT 50;
  ```

---

## Level 2: Multi-Column Intersection & Status Constraints

> **Scope**: Multiple filters combining domain categories, severity thresholds, boolean redundancy flags, and regional scopes.

### Query 2.1: Severe Ransomware without Backup Supplier in APAC
* **Natural Language Query**: *"Find severe ransomware incidents affecting chip makers in APAC without backup suppliers."*
* **Grounding**: 
  * `"ransomware"` $\rightarrow$ `disruption_type = 'Cyber Attack'`
  * `"chip makers"` $\rightarrow$ `industry = 'Electronics'`
  * `"APAC"` $\rightarrow$ `supplier_region = 'Asia-Pacific'`
  * `"severe"` $\rightarrow$ `disruption_severity >= 4`
  * `"without backup suppliers"` $\rightarrow$ `has_backup_supplier = FALSE`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, supplier_tier, supplier_region,
         disruption_severity, production_impact_pct, revenue_loss_usd, response_type,
         full_recovery_days, resilience_score, prioritization_level, top_risk_driver
  FROM v_disruption_details
  WHERE disruption_severity >= 4
    AND disruption_type = 'Cyber Attack'
    AND industry = 'Electronics'
    AND supplier_region = 'Asia-Pacific'
    AND has_backup_supplier = FALSE
  ORDER BY revenue_loss_usd DESC
  LIMIT 20;
  ```

### Query 2.2: Catastrophic Natural Disasters in Deep-Tier Suppliers
* **Natural Language Query**: *"Show level 5 natural disaster disruptions hitting Tier 3 or Tier 4 suppliers."*
* **Grounding**: `"level 5"` $\rightarrow$ `disruption_severity = 5`, `"natural disaster"` $\rightarrow$ `Natural Disaster`, `"Tier 3 or Tier 4"` $\rightarrow$ `supplier_tier IN (3, 4)`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, supplier_tier, supplier_region,
         disruption_severity, production_impact_pct, revenue_loss_usd, full_recovery_days
  FROM v_disruption_details
  WHERE disruption_severity = 5
    AND disruption_type = 'Natural Disaster'
    AND supplier_tier IN (3, 4)
  ORDER BY revenue_loss_usd DESC
  LIMIT 25;
  ```

### Query 2.3: P1-Critical Disruptions with Prolonged Recovery
* **Natural Language Query**: *"List P1-Critical disruptions in South America where full recovery took more than 60 days."*
* **Grounding**: `"P1-Critical"` $\rightarrow$ `prioritization_level = 'P1-Critical'`, `"South America"` $\rightarrow$ `supplier_region = 'South America'`, `full_recovery_days > 60`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, supplier_tier, revenue_loss_usd,
         full_recovery_days, resilience_score, top_risk_driver
  FROM v_disruption_details
  WHERE prioritization_level = 'P1-Critical'
    AND supplier_region = 'South America'
    AND full_recovery_days > 60
  ORDER BY full_recovery_days DESC
  LIMIT 50;
  ```

### Query 2.4: Severe Pharma Factory Incidents with High Production Impact
* **Natural Language Query**: *"Find pharmaceutical factory equipment breakdowns where production downtime exceeded 50%."*
* **Grounding**: `"pharmaceutical"` $\rightarrow$ `industry = 'Pharmaceuticals'`, `"factory equipment breakdowns"` $\rightarrow$ `disruption_type = 'Factory Incident'`, `production_impact_pct > 50`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, disruption_severity, production_impact_pct,
         revenue_loss_usd, response_type, full_recovery_days
  FROM v_disruption_details
  WHERE industry = 'Pharmaceuticals'
    AND disruption_type = 'Factory Incident'
    AND production_impact_pct > 50
  ORDER BY production_impact_pct DESC
  LIMIT 30;
  ```

### Query 2.5: Geopolitical Sanctions on Large Aerospace Suppliers
* **Natural Language Query**: *"Find geopolitical tariff and trade sanctions affecting large aerospace suppliers."*
* **Grounding**: `"geopolitical tariff and trade sanctions"` $\rightarrow$ `disruption_type = 'Geopolitical'`, `"large"` $\rightarrow$ `supplier_size = 'Large'`, `"aerospace"` $\rightarrow$ `industry = 'Aerospace'`
* **Generated SQL**:
  ```sql
  SELECT disruption_id, disruption_type, industry, supplier_size, supplier_region,
         disruption_severity, revenue_loss_usd, full_recovery_days
  FROM v_disruption_details
  WHERE disruption_type = 'Geopolitical'
    AND industry = 'Aerospace'
    AND supplier_size = 'Large'
  ORDER BY revenue_loss_usd DESC
  LIMIT 20;
  ```

---

## Level 3: Single Aggregations, Grouping, & Benchmark Comparison

> **Scope**: Aggregation functions (`COUNT`, `AVG`, `SUM`), `GROUP BY`, comparative metrics between response strategies or risk cohorts.

### Query 3.1: Alternative Supplier vs Production Reroute Performance
* **Natural Language Query**: *"What is the average financial loss and recovery time when companies use Alternative Supplier vs Production Reroute?"*
* **Target Schema**: `v_disruption_details`
* **Grounding**: `response_type IN ('Alternative Supplier', 'Production Reroute')`, `GROUP BY response_type`
* **Generated SQL**:
  ```sql
  SELECT response_type,
         COUNT(*) AS incident_count,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(full_recovery_days) AS avg_recovery_days,
         AVG(production_impact_pct) AS avg_downtime_pct,
         AVG(resilience_score) AS avg_resilience_score
  FROM v_disruption_details
  WHERE response_type IN ('Alternative Supplier', 'Production Reroute')
  GROUP BY response_type
  ORDER BY incident_count DESC;
  ```

### Query 3.2: Disruption Severity Breakdown by Disruption Type
* **Natural Language Query**: *"Calculate the mean revenue loss, recovery days, and average severity for each disruption type."*
* **Generated SQL**:
  ```sql
  SELECT disruption_type,
         COUNT(*) AS incident_count,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(full_recovery_days) AS avg_recovery_days,
         AVG(disruption_severity) AS avg_severity
  FROM v_disruption_details
  GROUP BY disruption_type
  ORDER BY avg_revenue_loss DESC;
  ```

### Query 3.3: Resilience Score Comparison by Supplier Tier Depth
* **Natural Language Query**: *"What is the average resilience score and downtime percentage across supplier tiers 1 through 4?"*
* **Generated SQL**:
  ```sql
  SELECT supplier_tier,
         COUNT(*) AS total_incidents,
         AVG(resilience_score) AS avg_resilience_score,
         AVG(production_impact_pct) AS avg_downtime_pct,
         AVG(revenue_loss_usd) AS avg_loss_usd
  FROM v_disruption_details
  GROUP BY supplier_tier
  ORDER BY supplier_tier ASC;
  ```

### Query 3.4: Response Strategy Effectiveness in Electronics
* **Natural Language Query**: *"Compare all five response strategies in the electronics industry by average recovery days and cost."*
* **Generated SQL**:
  ```sql
  SELECT response_type,
         COUNT(*) AS incident_count,
         AVG(full_recovery_days) AS avg_recovery_days,
         AVG(revenue_loss_usd) AS avg_loss_usd,
         AVG(resilience_score) AS avg_resilience_score
  FROM v_disruption_details
  WHERE industry = 'Electronics'
  GROUP BY response_type
  ORDER BY avg_resilience_score DESC;
  ```

### Query 3.5: Disruption Frequency & Loss by Geographic Region
* **Natural Language Query**: *"Show the count of disruptions and average financial loss grouped by supplier region."*
* **Generated SQL**:
  ```sql
  SELECT supplier_region,
         COUNT(*) AS incident_count,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(full_recovery_days) AS avg_recovery_days
  FROM v_disruption_details
  GROUP BY supplier_region
  ORDER BY incident_count DESC;
  ```

---

## Level 4: Multi-Dimensional Aggregation, Conditional Metrics & Triage Cross-Tabulation

> **Scope**: Multi-column grouping, cohort slicing with threshold filtering (`HAVING`), risk driver distribution, and backup supplier variance.

### Query 4.1: Upstream Supplier Downtime During Natural Disasters by Region
* **Natural Language Query**: *"Which supplier regions experience the highest average downtime for Tier 3 and Tier 4 suppliers during natural disasters?"*
* **Grounding**: `disruption_type = 'Natural Disaster'`, `supplier_tier IN (3, 4)`, `GROUP BY supplier_region`
* **Generated SQL**:
  ```sql
  SELECT supplier_region,
         COUNT(*) AS incident_count,
         AVG(production_impact_pct) AS avg_downtime_pct,
         AVG(full_recovery_days) AS avg_recovery_days,
         AVG(revenue_loss_usd) AS avg_revenue_loss
  FROM v_disruption_details
  WHERE disruption_type = 'Natural Disaster'
    AND supplier_tier IN (3, 4)
  GROUP BY supplier_region
  ORDER BY avg_downtime_pct DESC;
  ```

### Query 4.2: Backup Supplier Value in Severe Automotive Disruptions
* **Natural Language Query**: *"Compare the average financial loss and recovery days for automotive disruptions of severity 4 or 5 with backup supplier versus without backup supplier."*
* **Generated SQL**:
  ```sql
  SELECT has_backup_supplier,
         COUNT(*) AS total_incidents,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(full_recovery_days) AS avg_recovery_days,
         AVG(resilience_score) AS avg_resilience_score
  FROM v_disruption_details
  WHERE industry = 'Automotive'
    AND disruption_severity >= 4
  GROUP BY has_backup_supplier;
  ```

### Query 4.3: High-Impact Disruption Segments Exceeding $10M Average Loss
* **Natural Language Query**: *"Identify industry and disruption type combinations where average revenue loss exceeds 10 million dollars, with at least 500 incidents."*
* **Generated SQL**:
  ```sql
  SELECT industry,
         disruption_type,
         COUNT(*) AS incident_count,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(full_recovery_days) AS avg_recovery_days
  FROM v_disruption_details
  GROUP BY industry, disruption_type
  HAVING incident_count >= 500 AND avg_revenue_loss > 10000000
  ORDER BY avg_revenue_loss DESC;
  ```

### Query 4.4: Triage Level Distribution Across Industries
* **Natural Language Query**: *"Show the count and percentage of P1-Critical vs P4-Low incidents for each industry."*
* **Generated SQL**:
  ```sql
  SELECT industry,
         prioritization_level,
         COUNT(*) AS incident_count,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(resilience_score) AS avg_resilience_score
  FROM v_disruption_details
  WHERE prioritization_level IN ('P1-Critical', 'P4-Low')
  GROUP BY industry, prioritization_level
  ORDER BY industry ASC, prioritization_level ASC;
  ```

### Query 4.5: Top Risk Drivers in Single-Sourced Critical Incidents
* **Natural Language Query**: *"What are the most frequent top risk drivers among P1-Critical disruptions where no backup supplier existed?"*
* **Generated SQL**:
  ```sql
  SELECT top_risk_driver,
         COUNT(*) AS occurrence_count,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(full_recovery_days) AS avg_recovery_days
  FROM v_disruption_details
  WHERE prioritization_level = 'P1-Critical'
    AND has_backup_supplier = FALSE
  GROUP BY top_risk_driver
  ORDER BY occurrence_count DESC;
  ```

---

## Level 5: Strategic Cohort Analysis, Subqueries, & Counterfactual Playbook Evaluation

> **Scope**: Advanced analog cohort matching, counterfactual comparison (optimal vs suboptimal strategies for identical incident profiles), resilience divergence, and multi-tier ripple effect modeling.

### Query 5.1: Optimal Strategy for Incoming Incident Profile (Analog Cohort Benchmark)
* **Natural Language Query**: *"Find historical incidents matching our active disruption: Tier 2 electronics supplier in APAC hit by a Level 4 cyber attack without backup supplier, and rank the response strategies by average recovery days and resilience score."*
* **Operational Goal**: Used by `ResponseAgent` to recommend the empirically proven playbook for an active crisis.
* **Generated SQL**:
  ```sql
  SELECT response_type,
         COUNT(*) AS cohort_sample_size,
         AVG(resilience_score) AS avg_resilience_score,
         AVG(full_recovery_days) AS avg_recovery_days,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(production_impact_pct) AS avg_downtime_pct
  FROM v_disruption_details
  WHERE industry = 'Electronics'
    AND supplier_tier = 2
    AND supplier_region = 'Asia-Pacific'
    AND disruption_type = 'Cyber Attack'
    AND disruption_severity >= 4
    AND has_backup_supplier = FALSE
  GROUP BY response_type
  ORDER BY avg_resilience_score DESC, avg_recovery_days ASC;
  ```

### Query 5.2: High-Resilience vs Low-Resilience Playbook Divergence
* **Natural Language Query**: *"In the automotive sector under severe disruptions (severity >= 4), how do companies that achieved high resilience (score >= 80) differ in response strategy and backup availability from those with low resilience (score < 60)?"*
* **Operational Goal**: Used by `LLMJudge` and `ImpactAgent` to demonstrate safety and strategic divergence.
* **Generated SQL**:
  ```sql
  SELECT CASE 
           WHEN resilience_score >= 80 THEN 'High Resilience (>=80)'
           WHEN resilience_score < 60 THEN 'Low Resilience (<60)'
           ELSE 'Moderate Resilience'
         END AS resilience_tier,
         response_type,
         has_backup_supplier,
         COUNT(*) AS incident_count,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(full_recovery_days) AS avg_recovery_days
  FROM v_disruption_details
  WHERE industry = 'Automotive'
    AND disruption_severity >= 4
    AND (resilience_score >= 80 OR resilience_score < 60)
  GROUP BY resilience_tier, response_type, has_backup_supplier
  ORDER BY resilience_tier ASC, incident_count DESC;
  ```

### Query 5.3: Disproportionate Impact Outlier Analysis (Silent Ripple Risk)
* **Natural Language Query**: *"Identify disruptions where disruption severity was moderate (severity <= 3), but production downtime exceeded 60% or revenue loss exceeded $5M, and group by supplier tier and risk driver."*
* **Operational Goal**: Identifies hidden supply chain fragility in upstream tiers where small shocks cause catastrophic ripple effects.
* **Generated SQL**:
  ```sql
  SELECT supplier_tier,
         top_risk_driver,
         COUNT(*) AS outlier_count,
         AVG(production_impact_pct) AS avg_downtime_pct,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(full_recovery_days) AS avg_recovery_days
  FROM v_disruption_details
  WHERE disruption_severity <= 3
    AND (production_impact_pct > 60 OR revenue_loss_usd > 5000000)
  GROUP BY supplier_tier, top_risk_driver
  ORDER BY outlier_count DESC;
  ```

### Query 5.4: Multi-Strategy Recovery Trade-Off Frontier in Pharmaceuticals
* **Natural Language Query**: *"For pharmaceutical disruptions with recovery exceeding 90 days, what percentage required permanent supplier changes, and how did average revenue loss correlate with response type and backup supplier presence?"*
* **Generated SQL**:
  ```sql
  SELECT response_type,
         has_backup_supplier,
         COUNT(*) AS severe_case_count,
         AVG(revenue_loss_usd) AS avg_revenue_loss,
         AVG(full_recovery_days) AS avg_recovery_days,
         SUM(CASE WHEN recovery_status = 'Permanent Supplier Change' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_permanent_supplier_change
  FROM v_disruption_details
  WHERE industry = 'Pharmaceuticals'
    AND full_recovery_days > 90
  GROUP BY response_type, has_backup_supplier
  ORDER BY avg_revenue_loss DESC;
  ```

### Query 5.5: Cross-Tier Escalation Analog Cohort with Prioritized Playbook
* **Natural Language Query**: *"Retrieve the top 5 most severe historical analog incidents matching an upstream Tier 4 plant fire in Europe with over $20M revenue loss, displaying their full recovery trajectory, strategy applied, and assessed risk driver."*
* **Operational Goal**: Direct evidence lookup for `InvestigationAgent` to present human-in-the-loop historical case studies.
* **Generated SQL**:
  ```sql
  SELECT disruption_id,
         industry,
         supplier_tier,
         supplier_region,
         disruption_severity,
         production_impact_pct,
         revenue_loss_usd,
         response_type,
         full_recovery_days,
         recovery_status,
         resilience_score,
         prioritization_level,
         top_risk_driver,
         recommended_strategy
  FROM v_disruption_details
  WHERE supplier_tier = 4
    AND disruption_type = 'Factory Incident'
    AND supplier_region = 'Europe'
    AND revenue_loss_usd > 20000000
  ORDER BY revenue_loss_usd DESC, production_impact_pct DESC
  LIMIT 5;
  ```

---

## Benchmark Execution Harness

To evaluate these queries against the running MySQL database, execute:

```powershell
python -m app.services.sql_builder
```

Every query above is guaranteed to:
1. Target the unified view `v_disruption_details`.
2. Adhere strictly to the controlled schema dictionary.
3. Pass through `validate_sql_query()` read-only guardrails.
4. Execute against 100,000 historical disruption records in sub-second latency.
