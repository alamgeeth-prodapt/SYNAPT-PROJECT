import asyncio
import json
from app.services.synapt_service import SynaptService

async def test_fetch_classes():
    print("=== Testing Synapt Trident MCP for Uploaded Column Classes Doc ===")
    async with SynaptService() as syn:
        # 1. Check stats
        stats = await syn.get_stats()
        print(f"\n[Provider Stats]:")
        print(f"  Documents: {stats.get('doc_count')}")
        print(f"  Nodes: {stats.get('nodes')}")
        print(f"  Chunks: {stats.get('chunks')}")
        print(f"  Counts by label: {stats.get('counts_by_label')}")
        
        # 2. Search for documents
        print("\n[Document Search]:")
        docs_res = await syn.search("document filename schema classes dictionary")
        print(f"Search results count: {len(docs_res) if isinstance(docs_res, list) else type(docs_res)}")
        if isinstance(docs_res, list):
            for i, d in enumerate(docs_res[:5]):
                print(f"  Doc {i+1}: {d}")

        # 3. Targeted queries for column classes
        test_questions = [
            "What are the column classes and categories for the supply chain disruption tables?",
            "What are the discrete classes for disruption_type, industry, supplier_region, and response_type?",
            "List all categorical column values and allowed enum classes."
        ]

        for q in test_questions:
            print(f"\n--- Query: '{q}' ---")
            ans = await syn.query(q, top_k=5)
            # Write answer or snippet safely
            if isinstance(ans, dict):
                answer_text = ans.get("answer") or ans.get("result") or ans.get("response") or str(ans)
                print(f"Result keys: {list(ans.keys())}")
                if "answer" in ans:
                    print(f"Answer snippet: {str(ans['answer'])[:500]}...")
                elif "context" in ans:
                    print(f"Context snippet: {str(ans['context'])[:500]}...")
            elif isinstance(ans, str):
                print(f"Answer snippet: {ans[:500]}...")
            else:
                print(f"Response type: {type(ans)}, snippet: {str(ans)[:500]}")

if __name__ == "__main__":
    asyncio.run(test_fetch_classes())
