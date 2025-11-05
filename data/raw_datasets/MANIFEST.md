# Dataset Download Manifest

**Generated**: 2025-11-04T10:20:00

## Summary
- **Successfully Downloaded**: 12/13
- **Failed**: 1/13 (requires authentication)
- **Total Storage**: 2.1 GB

## Successfully Downloaded Datasets

| Tier | ID | Name | Size | Format | Source |
|------|----|----- |------|--------|--------|
| 1 | `bipia` | Microsoft BIPIA | 2.5M | JSON/JSONL | https://github.com/microsoft/BIPIA |
| 1 | `llmail_inject` | Microsoft LLMail-Inject | 411M | Parquet | microsoft/llmail-inject-challenge |
| 1 | `tensortrust` | TensorTrust | 16M | Mixed | https://github.com/HumanCompatibleAI/tensor-trust.git |
| 1 | `dan_jailbreak` | DAN Jailbreak | 52M | Mixed | https://github.com/verazuo/jailbreak_llms.git |
| 2 | `harmbench` | HarmBench | 469M | Mixed | https://github.com/centerforaisafety/HarmBench.git |
| 2 | `wildjailbreak` | WildJailbreak | 101M | Mixed | https://github.com/allenai/wildteaming.git |
| 2 | `gandalf_ignore` | Gandalf Ignore Instructions | 64K | Parquet | Lakera/gandalf_ignore_instructions |
| 2 | `mosscap` | Mosscap Prompt Injection | 61M | Parquet | Lakera/mosscap_prompt_injection |
| 2 | `alert` | ALERT | 978M | Mixed | https://github.com/Babelscape/ALERT.git |
| 3 | `jailbreakbench` | JailbreakBench | 4.0M | Mixed | https://github.com/JailbreakBench/jailbreakbench.git |
| 3 | `deepset_injection` | deepset prompt-injections | 64K | Parquet | deepset/prompt-injections |
| 3 | `open_prompt_injection` | Open-Prompt-Injection | 1.8M | Mixed | https://github.com/liu00222/Open-Prompt-Injection.git |

### Dataset Statistics

**By Tier:**
- Tier 1 (Must have): 4/5 (80%)
- Tier 2 (High value): 5/5 (100%)
- Tier 3 (Supplementary): 3/3 (100%)

**By Source Type:**
- HuggingFace: 4 datasets (llmail_inject, gandalf_ignore, mosscap, deepset_injection)
- GitHub: 8 datasets (bipia, tensortrust, dan_jailbreak, harmbench, wildjailbreak, alert, jailbreakbench, open_prompt_injection)

**Total Prompts (estimated):**
- Microsoft LLMail-Inject: 461,640 prompts
- Mosscap Prompt Injection: 278,945 prompts
- Gandalf Ignore Instructions: 1,000 prompts
- deepset prompt-injections: 662 prompts
- BIPIA: 15+ attack categories across multiple domains
- Other GitHub repos: Thousands more (see individual READMEs)

## Failed Downloads

### HackAPrompt (`hackaprompt`)
**Reason**: Gated dataset requiring HuggingFace authentication

**Manual steps required:**
```bash
# Login to HuggingFace
huggingface-cli login

# Then run Python to download:
python << 'EOF'
from datasets import load_dataset
from pathlib import Path

output_dir = Path("data/raw_datasets/hackaprompt")
output_dir.mkdir(parents=True, exist_ok=True)

dataset = load_dataset("hackaprompt/hackaprompt-dataset")
for split_name, split_data in dataset.items():
    parquet_path = output_dir / f"{split_name}.parquet"
    split_data.to_parquet(str(parquet_path))
    print(f"Saved {split_name}: {len(split_data)} rows")
EOF
```

## Storage Location
```
data/raw_datasets/
├── bipia/                      # 2.5M - Microsoft BIPIA
├── llmail_inject/              # 411M - Microsoft LLMail-Inject
├── tensortrust/                # 16M - TensorTrust
├── dan_jailbreak/              # 52M - DAN Jailbreak
├── hackaprompt/                # FAILED - requires auth
├── harmbench/                  # 469M - HarmBench
├── wildjailbreak/              # 101M - WildJailbreak
├── gandalf_ignore/             # 64K - Gandalf Ignore
├── mosscap/                    # 61M - Mosscap
├── alert/                      # 978M - ALERT
├── jailbreakbench/             # 4.0M - JailbreakBench
├── deepset_injection/          # 64K - deepset
└── open_prompt_injection/      # 1.8M - Open-Prompt-Injection
```

## Dataset Details

### Tier 1 - Must Have Datasets

**Microsoft BIPIA** (2.5M)
- Benchmark for Indirect Prompt Injection Attacks
- Multiple domains: email, code, table, QA, abstract
- Train/test splits
- 15+ attack categories
- Status: ✓ Downloaded from GitHub

**Microsoft LLMail-Inject** (411M)
- 461,640 prompt injection examples
- Phase 1 & Phase 2 splits
- Email-based prompt injection scenarios
- Status: ✓ Downloaded from HuggingFace

**TensorTrust** (16M)
- Adversarial prompt dataset from tensortrust.ai
- Competitive prompt hacking data
- Status: ✓ Downloaded from GitHub

**DAN Jailbreak** (52M)
- "Do Anything Now" jailbreak prompts
- Multiple jailbreak techniques
- Status: ✓ Downloaded from GitHub

**HackAPrompt** (FAILED)
- Competitive prompt hacking dataset
- Status: ✗ Requires HuggingFace authentication

### Tier 2 - High Value Datasets

**HarmBench** (469M)
- Comprehensive harm benchmark
- Multiple harm categories
- 19 data files
- Status: ✓ Downloaded from GitHub

**WildJailbreak** (101M)
- Real-world jailbreak attempts
- From Allen AI
- 6 data files
- Status: ✓ Downloaded from GitHub

**Gandalf Ignore Instructions** (64K)
- 1,000 prompts designed to bypass instruction-following
- Train/validation/test splits
- Status: ✓ Downloaded from HuggingFace

**Mosscap Prompt Injection** (61M)
- 278,945 prompt injection examples
- Multi-level difficulty
- Train/validation/test splits
- Status: ✓ Downloaded from HuggingFace

**ALERT** (978M)
- Adversarial Language Evaluation with Retrieval Tasks
- 41 data files
- Large-scale benchmark
- Status: ✓ Downloaded from GitHub

### Tier 3 - Supplementary Datasets

**JailbreakBench** (4.0M)
- Systematic jailbreak evaluation
- 2 data files
- Status: ✓ Downloaded from GitHub

**deepset prompt-injections** (64K)
- 662 labeled prompt injection examples
- Binary classification (injection vs. legitimate)
- Status: ✓ Downloaded from HuggingFace

**Open-Prompt-Injection** (1.8M)
- Open-source prompt injection collection
- 20 data files
- Status: ✓ Downloaded from GitHub

## Verification Status

All downloaded datasets have been verified:
- **HuggingFace datasets**: Parquet files can be loaded with pandas
- **GitHub repos**: Valid git repositories with data files
- **Sample data**: First 10 rows extracted for inspection

## Usage Notes

1. **Data Integrity**: All datasets are in their original format, no transformations applied
2. **Git Ignored**: All dataset files are gitignored and not committed to repository
3. **Individual READMEs**: Each dataset directory contains a README with:
   - Source information
   - Download date
   - License information
   - Citation information
   - Dataset structure and statistics

4. **Authentication**: For gated datasets (HackAPrompt), set up HuggingFace CLI:
   ```bash
   huggingface-cli login
   ```

5. **Updates**: To re-download a dataset, delete its directory and re-run the download script

## Download Scripts

- **Main script**: `scripts/download_datasets.py`
- **Additional datasets**: `scripts/download_additional_datasets.py`

To download all datasets:
```bash
python scripts/download_datasets.py
python scripts/download_additional_datasets.py
```

## Research Applications

These datasets are intended for:
- Prompt injection detection research
- Jailbreak prevention
- Adversarial prompt robustness evaluation
- Safety alignment testing
- Red teaming LLM applications

## License Compliance

Each dataset has its own license. Please refer to individual dataset READMEs and source repositories for license information before use.

## Next Steps

To complete the dataset collection:

1. **HackAPrompt** (requires manual intervention):
   - Authenticate with HuggingFace: `huggingface-cli login`
   - Request access to gated dataset at: https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
   - Wait for approval
   - Download using the Python script provided above

2. **Verify existing datasets** (OR-Bench, system-prompt-leakage, Alignment-Lab):
   - Check if these are already in the codebase
   - Document their sources
   - Add to this manifest

## Changelog

- **2025-11-04**: Initial download of 12/13 datasets (2.1 GB total)
  - Successfully downloaded all Tier 2 and Tier 3 datasets
  - Successfully downloaded 4/5 Tier 1 datasets
  - HackAPrompt requires authentication (pending)
