#!/usr/bin/env python3
"""Evaluation and visual comparison script for Context Memory Recall.
Tests both FTS5 BM25 keyword matching and sqlite-vec semantic search
against real ADR files in docs/ai/adr/.
"""

import os
import sys
from pathlib import Path

# Ensure tools/ is on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import memory_engine as me
import memory_rebuild as mr

TEST_CASES = [
    {
        "id": "TC-01",
        "type": "Keyword Match (Exact)",
        "query": "sqlite-vec FTS5 fallback latency budget",
        "expected_top": "ADR-002",
        "description": "Both FTS5 and Vector should easily locate ADR-002 via exact terms."
    },
    {
        "id": "TC-02",
        "type": "Semantic Concept (No exact keywords)",
        "query": "How do we prevent contaminating the developer operating system with heavy machine learning packages?",
        "expected_top": "ADR-001",
        "description": "Does NOT contain 'isolated' or 'venv'. Vector should excel; FTS5 will struggle."
    },
    {
        "id": "TC-03",
        "type": "Architectural Design (Semantic)",
        "query": "Where is project knowledge permanently saved so team members and other AI tools can share it?",
        "expected_top": "ADR-003",
        "description": "Concepts: cross-agent sharing, git tracking, persistent canonical storage."
    },
    {
        "id": "TC-04",
        "type": "Out-of-Domain (Negative check)",
        "query": "Kubernetes helm chart deployment and ingress controller ingress gateway configuration",
        "expected_top": None,
        "description": "Should yield 0 FTS5 hits and low vector similarity (high distance > 0.65)."
    }
]


def print_separator(char="=", length=90):
    print(char * length)


def run_evaluation():
    print_separator("=")
    print("🧠 CONTEXT MEMORY RECALL EVALUATION (FTS5 vs Vector Cosine)")
    print(f"📁 Project Root: {ROOT}")
    print_separator("=")

    # 1. Rebuild memory database from Markdown
    print("\n[Step 1] Rebuilding database index from docs/ai/adr/...")
    count = mr.rebuild(str(ROOT))
    print(f"  Indexed {count} document(s) into memory.db")

    conn = me.connect(str(ROOT))
    vec_loaded = me._load_vec_extension(conn)
    model = me._get_fastembed_model()
    print(f"  • sqlite-vec extension: {'✅ AVAILABLE' if vec_loaded else '❌ UNAVAILABLE'}")
    print(f"  • fastembed backend:    {'✅ AVAILABLE' if model else '❌ UNAVAILABLE'}")

    if not (vec_loaded and model):
        print("\n⚠️ WARNING: Run this script with ~/.gemini/venv/bin/python or ~/.claude/venv/bin/python to enable vector search!")

    # 2. Run Test Cases
    print_separator("-")
    print(f"{'ID':<6} | {'Query / Category':<45} | {'Mode':<8} | {'Top Match':<20} | {'Score/Dist':<10}")
    print_separator("-")

    for tc in TEST_CASES:
        query = tc["query"]
        print(f"\n{tc['id']:<6} | Query: \"{query[:42]}...\"")
        print(f"       | Type: {tc['type']} (Expected: {tc['expected_top']})")

        # A. FTS5 BM25 search
        fts_hits = me._fts_query(conn, query, k=3)
        if fts_hits:
            top_fts = fts_hits[0]
            title_short = (top_fts['title'] or 'untitled')[:20]
            score_str = f"bm25:{top_fts['score']:.2f}"
            print(f"       | -> FTS5 Keyword Match:  {title_short:<20} | {score_str:<10}")
        else:
            print(f"       | -> FTS5 Keyword Match:  {'[NO HITS]':<20} | {'N/A':<10}")

        # B. Semantic Vector search
        vec_res = me.query(conn, str(ROOT), query, k=3, budget_ms=None)
        if not vec_res["degraded"] and vec_res["hits"]:
            top_vec = vec_res["hits"][0]
            title_short = (top_vec['title'] or 'untitled')[:20]
            dist_str = f"dist:{top_vec['distance']:.4f}"
            print(f"       | -> Semantic Vector:     {title_short:<20} | {dist_str:<10}")
        elif vec_res["degraded"]:
            print(f"       | -> Semantic Vector:     [DEGRADED: {vec_res['reason']}]")
        else:
            print(f"       | -> Semantic Vector:     {'[NO HITS]':<20} | {'N/A':<10}")

        # Assessment
        print(f"       | Insight: {tc['description']}")

    print_separator("=")
    print("✅ Evaluation completed.\n")


if __name__ == "__main__":
    run_evaluation()
