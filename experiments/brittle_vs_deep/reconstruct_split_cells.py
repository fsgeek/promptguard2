#!/usr/bin/env python3
"""Reconstruct the split-cell population behind RESULT_two_failure_modes.md.

WHY THIS EXISTS
---------------
RESULT_two_failure_modes.md reports an 86/14 dual-judge split (72 agree / 12 split
on 84 full-context reply-judgements) and then a third-judge re-grade that "broke
12/12 ties." The 86/14 table reconstructs exactly from uplift_audit_results.json
(this script proves it). The THIRD-JUDGE step does NOT: commits 917e52f and 336aab3
are markdown-only; no qwen-2.5-72b verdict was ever persisted. So the "12/12 ties
broken" claim — the load-bearing evidence for Paper 5's thesis that a third judge
dissolves the residual — is currently UNBACKED by any data artifact.

This script regenerates what IS recoverable (the 12 split cells and the agree
breakdown) so the third-judge gap experiment runs against a fixed, committed
population instead of a remembered one.

CRITICAL AXIS NOTE
------------------
The 12 splits live on the THREE-WAY `outcome` label (real_harm / lucky_pivot /
refuse_or_empty), NOT the boolean `actionable` field (which yields only 3 splits).
The third-judge test must be pre-registered on the same `outcome` axis.

Run: python3 reconstruct_split_cells.py
Writes: split_cells.json (the frozen 12-cell population for the third-judge run)
"""
import json
from collections import Counter
from pathlib import Path

SRC = Path(__file__).parent / "uplift_audit_results.json"
OUT = Path(__file__).parent / "split_cells.json"


def reply_judgements(data):
    """Yield (id, cell_name, model, {judge: verdict}) for every full-context
    reply that received >=2 judge verdicts."""
    for item in data:
        for cell_name, cell in (item.get("cells") or {}).items():
            judged = cell.get("judged") or {}
            for model, jd in judged.items():
                judges = {k: v for k, v in jd.items() if k.endswith("_j")}
                if len(judges) < 2:
                    continue
                yield item["id"], cell_name, model, judges, cell


def main():
    data = json.loads(SRC.read_text())
    rows = list(reply_judgements(data))

    agree = Counter()
    splits = []
    for _id, cname, model, judges, cell in rows:
        outcomes = [v.get("outcome") for v in judges.values()]
        if None in outcomes:
            continue
        if len(set(outcomes)) == 1:
            agree[outcomes[0]] += 1
        else:
            splits.append(
                {
                    "id": _id,
                    "cell": cname,
                    "model": model,
                    "judge_outcomes": {jn: judges[jn].get("outcome") for jn in judges},
                    "trigger": cell.get("trigger"),
                    "reply": cell.get("replies", {}).get(model),
                }
            )

    total = sum(agree.values()) + len(splits)
    print(f"total full-context reply-judgements: {total}")
    print(f"agree breakdown (outcome axis): {dict(agree)}")
    print(f"split (residual): {len(splits)}")
    print(
        f"agreement rate: {sum(agree.values())/total:.3f} "
        f"(doc claims 86% / 14% split)"
    )

    # Independent cross-check on the boolean axis, to document the axis trap.
    bool_split = 0
    for _id, cname, model, judges, cell in rows:
        acts = [v.get("actionable") for v in judges.values()]
        if None in acts:
            continue
        if len(set(acts)) > 1:
            bool_split += 1
    print(
        f"\n[axis check] boolean 'actionable' splits: {bool_split} "
        f"(NOT the residual; the residual is the {len(splits)} outcome-axis splits)"
    )

    OUT.write_text(json.dumps({"agree": dict(agree), "splits": splits}, indent=2))
    print(f"\nwrote {OUT.name}: {len(splits)} split cells frozen for the third-judge run")
    print(
        "NOTE: the prior 'third judge broke 12/12' result has NO stored verdicts; "
        "the third-judge gap experiment must generate and persist them."
    )


if __name__ == "__main__":
    main()
