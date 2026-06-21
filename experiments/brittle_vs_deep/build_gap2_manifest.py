#!/usr/bin/env python3
"""gap-2 sampler: freeze the TensorTrust manifest BEFORE any dual-judging.

Strata are pre-committed in prereg_gap2_tensortrust_cold.md (sealed 2026-06-20).
A: regex-positive AND attacker_input lacks access_code verbatim (granted w/o password)
B: long/ambiguous output (len(llm_output) > 200)
C: random baseline
150 each, llm_choice == GPT_35_TURBO_0613, fixed seed. Reservoir-sample in one
stream pass (file is 563k records, ~1.6GB decompressed — never hold it all).
"""
import bz2, json, random, os

SRC = "/home/tony/projects/promptguard/promptguard2/data/raw_datasets/tensortrust-data/raw-data/v2/raw_dump_attacks.jsonl.bz2"
OUT = os.path.join(os.path.dirname(__file__), "gap2_manifest.json")
N_PER = 150
SEED = 20260620
MODEL = "GPT_35_TURBO_0613"

def in_A(d):
    if not d.get("output_is_access_granted"):
        return False
    ac = (d.get("access_code") or "").strip().lower()
    ai = (d.get("attacker_input") or "").lower()
    return bool(ac) and ac not in ai  # granted, but password not literally present

def in_B(d):
    return len(str(d.get("llm_output") or "")) > 200

# Reservoir sampling per stratum in a single pass.
rng = random.Random(SEED)
res = {"A": [], "B": [], "C": []}
seen = {"A": 0, "B": 0, "C": 0}
total = 0

def offer(key, rec):
    seen[key] += 1
    r = res[key]
    if len(r) < N_PER:
        r.append(rec)
    else:
        j = rng.randint(0, seen[key] - 1)
        if j < N_PER:
            r[j] = rec

KEEP = ("attack_id", "opening_defense", "attacker_input", "closing_defense",
        "llm_output", "output_is_access_granted", "access_code", "llm_choice")

with bz2.open(SRC, "rt") as f:
    for line in f:
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("llm_choice") != MODEL:
            continue
        if not str(d.get("llm_output") or "").strip():
            continue  # need a response to judge
        total += 1
        rec = {k: d.get(k) for k in KEEP}
        # C = every qualifying record is eligible for the random baseline
        offer("C", rec)
        if in_A(d):
            offer("A", rec)
        elif in_B(d):  # elif: B is "long AND not already an A case" to keep strata disjoint
            offer("B", rec)

manifest = {
    "sealed_prereg": "prereg_gap2_tensortrust_cold.md",
    "source": SRC,
    "seed": SEED,
    "model_filter": MODEL,
    "n_per_stratum": N_PER,
    "total_qualifying_records_streamed": total,
    "stratum_eligible_counts": seen,
    "strata": {k: res[k] for k in ("A", "B", "C")},
}
with open(OUT, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"streamed {total} {MODEL} records with non-empty output")
print(f"eligible per stratum: {seen}")
print(f"sampled: A={len(res['A'])} B={len(res['B'])} C={len(res['C'])}")
print(f"wrote {OUT}")
