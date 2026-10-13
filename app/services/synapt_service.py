"""
Async client utility wrapping the Synapt Trident MCP server.

Wraps the auth + JSON-RPC handshake pattern already proven in
`synapt_mcp_client.py` / `test_mcp_tools.py` into a reusable class with:
  - lazy authentication + MCP `initialize` handshake (done once, reused)
  - automatic re-auth on an expired/rejected token
  - an in-memory cache for `trident_get_schema` (schema rarely changes
    within a session, and the architecture doc calls for "safe caching
    for schema lookups")

Required environment variables (already present in `.env`):
    SYNAPT_AUTH_BASE       token endpoint
    SYNAPT_MCP_URL         MCP JSON-RPC endpoint
    SYNAPT_USERNAME
    SYNAPT_PASSWORD
    SYNAPT_PROVIDER_ID     default provider_id used when one isn't passed in
Optional:
    SYNAPT_TOP_K           default top_k for search/query calls (default 5)
    SYNAPT_GRAPH_HOPS      default graph_hops for trident_query (default None)
"""

import asyncio
import json
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


class SynaptServiceError(RuntimeError):
    pass


class SynaptService:
    def __init__(self):
        self.auth_url = os.getenv("SYNAPT_AUTH_BASE")
        self.mcp_url = os.getenv("SYNAPT_MCP_URL")
        self.username = os.getenv("SYNAPT_USERNAME")
        self.password = os.getenv("SYNAPT_PASSWORD")
        self.default_provider_id = os.getenv("SYNAPT_PROVIDER_ID")
        self.sop_provider_id = os.getenv("SYNAPT_SOP_PROVIDER_ID", "supply_chain_sop")
        self.default_top_k = int(os.getenv("SYNAPT_TOP_K", "5"))
        graph_hops = os.getenv("SYNAPT_GRAPH_HOPS")
        self.default_graph_hops = int(graph_hops) if graph_hops else None

        if not all([self.auth_url, self.mcp_url, self.username, self.password]):
            raise RuntimeError(
                "Missing SYNAPT_* settings in .env: "
                "SYNAPT_AUTH_BASE, SYNAPT_MCP_URL, SYNAPT_USERNAME, SYNAPT_PASSWORD are required."
            )

        self._client = httpx.AsyncClient(timeout=30, verify=False)
        self._token: str | None = None
        self._initialized = False
        self._schema_cache: dict[str, dict] = {}
        self._classes_cache: dict[str, list] = {}
        self._rpc_id = 0

    async def aclose(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.aclose()

    # ------------------------------------------------------------------
    # Auth + handshake
    # ------------------------------------------------------------------

    async def _authenticate(self) -> str:
        response = await self._client.post(
            self.auth_url,
            data={"username": self.username, "password": self.password},
        )
        if not response.is_success:
            raise SynaptServiceError(
                f"Synapt authentication failed: HTTP {response.status_code}"
            )

        token = response.json().get("access_token")
        if not token:
            raise SynaptServiceError("Synapt authentication response had no access_token.")

        self._token = token
        return token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

    @staticmethod
    def _parse_response(response: httpx.Response) -> list[dict]:
        content_type = response.headers.get("Content-Type", "")

        if "text/event-stream" in content_type:
            events = []
            for line in response.text.splitlines():
                if line.startswith("data:"):
                    data = line[len("data:"):].strip()
                    if data:
                        events.append(json.loads(data))
            return events

        try:
            return [response.json()]
        except ValueError:
            return []

    def _next_id(self) -> int:
        self._rpc_id += 1
        return self._rpc_id

    async def _send_rpc(
        self, method: str, request_id: int | None = None, params: dict | None = None
    ) -> list[dict]:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if request_id is not None:
            payload["id"] = request_id
        if params is not None:
            payload["params"] = params

        response = await self._client.post(self.mcp_url, headers=self._headers(), json=payload)

        if response.status_code == 401 and self._token is not None:
            # Token likely expired — re-authenticate once and retry.
            await self._authenticate()
            response = await self._client.post(self.mcp_url, headers=self._headers(), json=payload)

        if not response.is_success:
            raise SynaptServiceError(f"{method}: HTTP {response.status_code} — {response.text[:500]}")

        return self._parse_response(response)

    async def _ensure_session(self):
        if self._initialized:
            return

        if self._token is None:
            await self._authenticate()

        init_results = await self._send_rpc(
            "initialize",
            request_id=self._next_id(),
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "supply-chain-retriever", "version": "1.0.0"},
            },
        )
        for item in init_results:
            if "error" in item:
                raise SynaptServiceError(f"MCP initialization failed: {item['error']}")

        await self._send_rpc("notifications/initialized")
        self._initialized = True

    # ------------------------------------------------------------------
    # Generic tool call
    # ------------------------------------------------------------------

    @staticmethod
    def _unwrap(result: dict) -> Any:
        """
        FastMCP wraps tool results as either `structuredContent.result` or
        `content[0].text`, both of which are typically a JSON-encoded string.
        Return the parsed payload directly so callers get plain dicts/lists.
        """
        raw = None

        structured = result.get("structuredContent")
        if isinstance(structured, dict) and "result" in structured:
            raw = structured["result"]
        else:
            content = result.get("content")
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, dict) and first.get("type") == "text":
                    raw = first.get("text")

        if raw is None:
            return result

        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw

        return raw

    async def _call_tool(self, tool_name: str, arguments: dict) -> Any:
        await self._ensure_session()

        results = await self._send_rpc(
            "tools/call",
            request_id=self._next_id(),
            params={"name": tool_name, "arguments": arguments},
        )

        for item in results:
            if "error" in item:
                raise SynaptServiceError(f"{tool_name} error: {item['error']}")
            if "result" in item:
                return self._unwrap(item["result"])

        raise SynaptServiceError(f"{tool_name}: no result in MCP response.")

    def _provider(self, provider_id: str | None) -> str:
        provider_id = provider_id or self.default_provider_id
        if not provider_id:
            raise SynaptServiceError("provider_id was not supplied and SYNAPT_PROVIDER_ID is unset.")
        return provider_id

    # ------------------------------------------------------------------
    # Public tool wrappers
    # ------------------------------------------------------------------

    async def get_schema(self, provider_id: str | None = None, use_cache: bool = True) -> dict:
        """Get the knowledge graph schema, cached per provider_id within this instance."""
        provider_id = self._provider(provider_id)

        if use_cache and provider_id in self._schema_cache:
            return self._schema_cache[provider_id]

        result = await self._call_tool("trident_get_schema", {"provider_id": provider_id})
        self._schema_cache[provider_id] = result
        return result

    async def select_schema_for_task(self, query: str, provider_id: str | None = None) -> dict[str, Any]:
        """
        Queries Synapt Trident MCP knowledge graph to dynamically identify the relevant
        database view, filter columns, and projection structure for a user question.
        """
        known_columns = [
            "disruption_id",
            "disruption_type",
            "industry",
            "supplier_tier",
            "supplier_region",
            "supplier_size",
            "has_backup_supplier",
            "disruption_severity",
            "production_impact_pct",
            "revenue_loss_usd",
            "response_type",
            "response_time_days",
            "partial_recovery_days",
            "full_recovery_days",
            "permanent_supplier_change",
            "resilience_score",
            "prioritization_level",
            "top_risk_driver",
            "recommended_strategy",
        ]
        columns_str = ", ".join(known_columns)
        question = (
            f"Given the database schema for supply_chain_db and the view v_disruption_details "
            f"(columns: {columns_str}), "
            f"which filter columns and target view are relevant for the query: '{query}'? "
            f"Explicitly list the specific column names to filter on."
        )
        res = await self.query(question, top_k=3, provider_id=provider_id)
        raw_answer = res.get("answer", "") if isinstance(res, dict) else str(res)

        target_view = "v_disruption_details"
        if "disruptions" in raw_answer.lower() and "v_disruption_details" not in raw_answer.lower():
            target_view = "disruptions"

        found_cols = []
        for col in known_columns:
            if re.search(rf"\b{re.escape(col)}\b", raw_answer, re.IGNORECASE):
                found_cols.append(col)

        is_aggregation = any(
            re.search(rf"\b{re.escape(term)}\b", query, re.IGNORECASE)
            for term in ["average", "avg", "mean", "count", "sum", "rate", "compare", "breakdown", "group by"]
        )

        if is_aggregation:
            projection_cols = ["COUNT(*) AS incident_count"]
            if any(re.search(rf"\b{re.escape(t)}\b", query, re.IGNORECASE) for t in ["revenue", "financial", "loss"]):
                projection_cols.append("AVG(revenue_loss_usd) AS avg_revenue_loss")
            if any(re.search(rf"\b{re.escape(t)}\b", query, re.IGNORECASE) for t in ["recovery", "days", "time"]):
                projection_cols.append("AVG(full_recovery_days) AS avg_recovery_days")
            if any(re.search(rf"\b{re.escape(t)}\b", query, re.IGNORECASE) for t in ["impact", "downtime"]):
                projection_cols.append("AVG(production_impact_pct) AS avg_downtime_pct")
            if re.search(r"\bresilience\b", query, re.IGNORECASE):
                projection_cols.append("AVG(resilience_score) AS avg_resilience_score")
        else:
            projection_cols = [
                "disruption_id",
                "disruption_type",
                "industry",
                "supplier_tier",
                "supplier_region",
                "disruption_severity",
                "production_impact_pct",
                "revenue_loss_usd",
                "response_type",
                "full_recovery_days",
                "resilience_score",
                "prioritization_level",
                "top_risk_driver",
            ]

        return {
            "target_view": target_view,
            "filter_columns": sorted(list(set(found_cols))),
            "projection_columns": projection_cols,
            "is_aggregation": is_aggregation,
            "schema_source": "synapt_trident_mcp",
            "synapt_guidance": raw_answer,
        }

    async def get_column_classes(
        self,
        columns: list[str] | None = None,
        provider_id: str | None = None,
        use_cache: bool = True,
    ) -> dict[str, list]:
        """
        Dynamically retrieves controlled categorical classes for schema columns
        from the Synapt Trident MCP knowledge base, with in-memory caching.
        """
        if use_cache and self._classes_cache:
            if columns:
                return {col: self._classes_cache[col] for col in columns if col in self._classes_cache}
            return dict(self._classes_cache)

        question = (
            "What are all the controlled classes and categories for each column "
            "in the supply chain schema? List disruption_type, industry, supplier_region, "
            "supplier_tier, supplier_size, disruption_severity, and response_type."
        )
        res = await self.query(question, top_k=5, provider_id=provider_id)
        raw_answer = res.get("answer", "")

        ontology: dict[str, list] = {}
        current_col = None

        for line in raw_answer.splitlines():
            line = line.strip()
            if not line:
                continue

            col_match = re.match(r"^[-*]\s+\*\*([a-zA-Z0-9_]+)\*\*:", line)
            if col_match:
                current_col = col_match.group(1)
                ontology[current_col] = []
                continue

            if current_col:
                item_match = re.match(r"^[-*]\s+`([^`]+)`", line)
                if item_match:
                    val = item_match.group(1).strip()
                    if val.isdigit():
                        ontology[current_col].append(int(val))
                    else:
                        ontology[current_col].append(val)
                else:
                    if line.startswith("- **") or line.startswith("Note:"):
                        current_col = None

        if ontology:
            self._classes_cache.update(ontology)

        if columns:
            return {col: self._classes_cache[col] for col in columns if col in self._classes_cache}
        return dict(self._classes_cache)

    async def search(
        self,
        query: str,
        node_type: str = "",
        top_k: int | None = None,
        provider_id: str | None = None,
    ) -> dict:
        return await self._call_tool(
            "trident_search",
            {
                "provider_id": self._provider(provider_id),
                "query": query,
                "node_type": node_type,
                "top_k": top_k if top_k is not None else self.default_top_k,
            },
        )

    async def find_exact(
        self, name: str, node_type: str = "", provider_id: str | None = None
    ) -> dict:
        return await self._call_tool(
            "trident_find_exact",
            {"provider_id": self._provider(provider_id), "name": name, "node_type": node_type},
        )

    async def query(
        self,
        question: str,
        top_k: int | None = None,
        graph_hops: int | None = None,
        provider_id: str | None = None,
        **extra_params,
    ) -> dict:
        """Run a retrieval-augmented query (`trident_query`) against the knowledge base."""
        params = {
            "provider_id": self._provider(provider_id),
            "question": question,
            "top_k": top_k if top_k is not None else self.default_top_k,
            "graph_hops": graph_hops if graph_hops is not None else self.default_graph_hops,
            **extra_params,
        }
        return await self._call_tool("trident_query", params)

    async def get_stats(self, provider_id: str | None = None) -> dict:
        return await self._call_tool("trident_get_stats", {"provider_id": self._provider(provider_id)})

    async def cypher(self, query: str, provider_id: str | None = None) -> dict:
        """Run a read-only Cypher query against the graph."""
        return await self._call_tool(
            "trident_cypher", {"provider_id": self._provider(provider_id), "query": query}
        )

    async def get_node(
        self,
        node_id: str,
        include_chunks: bool = False,
        depth: int = 1,
        provider_id: str | None = None,
    ) -> dict:
        return await self._call_tool(
            "trident_get_node",
            {
                "provider_id": self._provider(provider_id),
                "node_id": node_id,
                "include_chunks": include_chunks,
                "depth": depth,
            },
        )

    async def traverse(
        self,
        node_id: str,
        edge_types: str = "",
        node_types: str = "",
        direction: str = "both",
        depth: int = 1,
        provider_id: str | None = None,
    ) -> dict:
        return await self._call_tool(
            "trident_traverse",
            {
                "provider_id": self._provider(provider_id),
                "node_id": node_id,
                "edge_types": edge_types,
                "node_types": node_types,
                "direction": direction,
                "depth": depth,
            },
        )

    async def get_chunks(
        self, query: str, top_k: int = 5, provider_id: str | None = None
    ) -> dict:
        return await self._call_tool(
            "trident_get_chunks",
            {"provider_id": self._provider(provider_id), "query": query, "top_k": top_k},
        )

    async def get_procedures(self, query: str = "", provider_id: str | None = None) -> dict:
        return await self._call_tool(
            "trident_get_procedures", {"provider_id": self._provider(provider_id), "query": query}
        )

    async def retrieve_sop_chunks(self, query: str, top_k: int = 5) -> dict[str, Any]:
        """
        Retrieves relevant SOP procedures and structured operational steps directly from
        Synapt Trident MCP using `trident_get_procedures` as the primary procedure-based engine.
        Falls back to semantic embedding chunks (`trident_get_chunks` / `trident_query`) if no
        structured procedures match the inquiry.
        """
        # Step 1: Query procedure-based tool (trident_get_procedures)
        procedures = []
        try:
            procs_call = await self.get_procedures(query=query, provider_id=self.sop_provider_id)
            if isinstance(procs_call, list) and procs_call:
                procedures = procs_call
        except Exception as e:
            print(f"trident_get_procedures error: {e}")

        if procedures:
            primary_proc = procedures[0]
            proc_name = primary_proc.get("name", "Standard Operating Procedure")
            proc_intent = primary_proc.get("intent", "")
            steps = primary_proc.get("steps", [])

            lines = [
                f"### Protocol: {proc_name}",
                f"**Operational Mandate:** {proc_intent}",
                "\n**Governing SOP Action Checklist:**",
            ]
            document_chunks = []
            formatted_chunks = {}

            for s in steps:
                s_num = s.get("step_number")
                s_desc = s.get("description", "")
                s_resp = s.get("responsibilities", "Operations Team")
                s_pre = s.get("pre_requisite", "")

                lines.append(f"{s_num}. **Step {s_num}:** {s_desc} *(Responsibility: {s_resp})*")

                c_id = f"{proc_name[:8].strip()}_Step_{s_num}"
                c_text = f"Step {s_num}: {s_desc} [Prerequisite: {s_pre or 'None'}] [Responsibility: {s_resp}]"
                document_chunks.append({
                    "chunk_id": c_id,
                    "text": c_text,
                    "source_file": proc_name,
                    "doc_type": "procedure_step",
                    "step_number": s_num,
                    "responsibilities": s_resp,
                })
                formatted_chunks[f"step_{s_num}_{c_id[:12]}"] = {
                    "chunk_id": c_id,
                    "source_document": proc_name,
                    "content": c_text,
                }

            # If secondary procedures were returned, append them as supporting reference chunks
            for p_idx, sec_proc in enumerate(procedures[1:3], 2):
                sec_name = sec_proc.get("name", f"Secondary Playbook {p_idx}")
                sec_intent = sec_proc.get("intent", "")
                sec_steps = sec_proc.get("steps", [])
                summary_text = f"Secondary Guideline: {sec_name}. Mandate: {sec_intent}. Key actions: " + "; ".join(
                    [f"Step {st.get('step_number')}: {st.get('description')[:120]}" for st in sec_steps[:3]]
                )
                document_chunks.append({
                    "chunk_id": f"PROC_SEC_{p_idx}",
                    "text": summary_text,
                    "source_file": sec_name,
                    "doc_type": "secondary_procedure",
                })
                formatted_chunks[f"playbook_{p_idx}"] = {
                    "chunk_id": f"PROC_SEC_{p_idx}",
                    "source_document": sec_name,
                    "content": summary_text,
                }

            live_answer = "\n".join(lines)
            return {
                "provider": self.sop_provider_id,
                "tool_used": "trident_get_procedures",
                "storage_system": "Synapt Trident Procedure Knowledge Graph",
                "query": query,
                "playbook_title": proc_name,
                "answer": live_answer,
                "synapt_live_answer": live_answer,
                "chunks_count": len(document_chunks),
                "procedures_count": len(procedures),
                "procedures": procedures,
                "document_chunks": document_chunks,
                "chunks": formatted_chunks,
                "source": "synapt_procedure_retriever",
            }

        # Step 2: Fallback to semantic query (trident_query + trident_get_chunks) if no procedures matched
        synapt_result = None
        raw_chunks = []
        try:
            synapt_result = await self.query(
                question=query,
                top_k=top_k,
                provider_id=self.sop_provider_id,
            )
        except Exception as e:
            synapt_result = {"error": f"Synapt query failed: {str(e)}"}

        try:
            chunks_call = await self.get_chunks(
                query=query,
                top_k=top_k,
                provider_id=self.sop_provider_id,
            )
            if isinstance(chunks_call, list):
                raw_chunks = chunks_call
        except Exception:
            if isinstance(synapt_result, dict) and synapt_result.get("chunks"):
                raw_chunks = synapt_result.get("chunks", [])

        formatted_chunks = {}
        document_chunks = []
        for idx, chunk in enumerate(raw_chunks):
            if isinstance(chunk, dict):
                c_id = chunk.get("chunk_id", f"chunk_{idx+1}")
                c_text = chunk.get("text", "").strip()
                c_src = chunk.get("source_file", "supply_chain_sop")
                c_type = chunk.get("doc_type", "sop")
                c_score = chunk.get("score")

                document_chunks.append({
                    "chunk_id": c_id,
                    "text": c_text,
                    "source_file": c_src,
                    "doc_type": c_type,
                    "score": c_score,
                })
                formatted_chunks[f"chunk_{idx+1}_{c_id[:12]}"] = {
                    "chunk_id": c_id,
                    "source_document": c_src,
                    "content": c_text,
                }

        live_answer = synapt_result.get("answer") if isinstance(synapt_result, dict) else None
        chunks_used_ids = synapt_result.get("chunks_used", []) if isinstance(synapt_result, dict) else []

        return {
            "provider": self.sop_provider_id,
            "tool_used": "trident_query",
            "storage_system": "Synapt Trident Vector & Graph Store",
            "query": query,
            "playbook_title": "Standard Operating Procedures",
            "answer": live_answer,
            "synapt_live_answer": live_answer,
            "chunks_count": len(document_chunks),
            "chunks_used_ids": chunks_used_ids,
            "document_chunks": document_chunks,
            "chunks": formatted_chunks if formatted_chunks else {
                "chunk_1_synapt_answer": live_answer or "No matching chunks found in Synapt embedding store."
            },
            "source": "synapt_embedding_retriever",
        }


async def _demo():
    async with SynaptService() as synapt:
        stats = await synapt.get_stats()
        print("trident_get_stats:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))

        schema = await synapt.get_schema()
        print("\ntrident_get_schema (first call, uncached):")
        print(json.dumps(schema, indent=2, ensure_ascii=False)[:1000])

        answer = await synapt.query(
            "What factors are associated with severe supply chain disruptions, "
            "and what recovery strategies are described in the available knowledge?"
        )
        print("\ntrident_query:")
        print(json.dumps(answer, indent=2, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    asyncio.run(_demo())
