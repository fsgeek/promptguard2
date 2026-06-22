#!/usr/bin/env python3
"""gap-3 sampler: freeze the MHJ manifest BEFORE generation.

MHJ is attacks-only (537 convs, system+user turns, NO assistant). We freeze each
conversation's ordered messages + the red-teamer's submission_message as the covert goal.
All 537 (small enough to run fully). Seed fixed only matters if we sub-sample; we don't.
"""
import csv, json, os

SRC = "/home/tony/projects/promptguard/promptguard2/data/raw_datasets/MHJ/harmbench_behaviors.csv"
OUT = os.path.join(os.path.dirname(__file__), "gap3_manifest.json")

rows = list(csv.DictReader(open(SRC)))
cells = []
for idx, r in enumerate(rows):
    msgs = []
    for i in range(0, 101):
        raw = r.get(f"message_{i}", "")
        if not raw:
            continue
        try:
            m = json.loads(raw)
        except Exception:
            continue
        role = m.get("role")
        body = m.get("body", "")
        if role in ("system", "user") and body:
            msgs.append({"role": role, "content": body})
    if not any(m["role"] == "user" for m in msgs):
        continue  # need at least one user turn
    cells.append({
        "mhj_id": idx,
        "question_id": r.get("question_id"),
        "tactic": r.get("tactic"),
        "source": r.get("Source"),
        "goal": r.get("submission_message", ""),  # red-teamer's stated objective
        "messages": msgs,
        "n_user_turns": sum(1 for m in msgs if m["role"] == "user"),
    })

manifest = {
    "sealed_prereg": "prereg_gap3_mhj_nofact.md",
    "source": SRC,
    "n_conversations": len(cells),
    "note": "attacks-only; responses GENERATED at run time (mistral-medium-3.1)",
    "cells": cells,
}
json.dump(manifest, open(OUT, "w"), indent=2)
print(f"froze {len(cells)} conversations -> {OUT}")
print("turn distribution (user turns):",
      {k: sum(1 for c in cells if c['n_user_turns'] == k) for k in sorted(set(c['n_user_turns'] for c in cells))})
