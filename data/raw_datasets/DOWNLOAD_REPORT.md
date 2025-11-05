# Dataset Download Report

**Date**: November 4, 2025
**Status**: 12/13 datasets successfully downloaded
**Total Storage**: 2.1 GB

---

## Executive Summary

Successfully downloaded 12 out of 13 high-quality adversarial prompt datasets for prompt injection research. Only 1 dataset (HackAPrompt) requires manual authentication with HuggingFace.

### Success Rate by Tier
- **Tier 1 (Must have)**: 4/5 (80%) - Missing HackAPrompt
- **Tier 2 (High value)**: 5/5 (100%) - All downloaded
- **Tier 3 (Supplementary)**: 3/3 (100%) - All downloaded

---

## Successfully Downloaded (12/13)

### Ordered by Size

| # | Dataset | Size | Format | Source | Tier |
|---|---------|------|--------|--------|------|
| 1 | ALERT | 978M | Mixed | GitHub | 2 |
| 2 | HarmBench | 469M | Mixed | GitHub | 2 |
| 3 | Microsoft LLMail-Inject | 411M | Parquet | HuggingFace | 1 |
| 4 | WildJailbreak | 101M | Mixed | GitHub | 2 |
| 5 | Mosscap Prompt Injection | 61M | Parquet | HuggingFace | 2 |
| 6 | DAN Jailbreak | 52M | Mixed | GitHub | 1 |
| 7 | TensorTrust | 16M | Mixed | GitHub | 1 |
| 8 | JailbreakBench | 4.0M | Mixed | GitHub | 3 |
| 9 | Microsoft BIPIA | 3.5M | JSON/JSONL | GitHub | 1 |
| 10 | Open-Prompt-Injection | 1.8M | Mixed | GitHub | 3 |
| 11 | Gandalf Ignore Instructions | 64K | Parquet | HuggingFace | 2 |
| 12 | deepset prompt-injections | 64K | Parquet | HuggingFace | 3 |

### Key Datasets Acquired

**Largest Datasets:**
- **ALERT** (978M): Adversarial Language Evaluation with Retrieval Tasks - 41 data files
- **HarmBench** (469M): Comprehensive harm benchmark - 19 data files
- **Microsoft LLMail-Inject** (411M): 461,640 prompt injection examples

**Most Valuable for Prompt Injection Research:**
- **Microsoft BIPIA**: Benchmark for Indirect Prompt Injection Attacks (15+ attack categories)
- **Microsoft LLMail-Inject**: Email-based prompt injection scenarios
- **Mosscap Prompt Injection**: 278,945 examples with multi-level difficulty

**Jailbreak-Specific:**
- **DAN Jailbreak**: "Do Anything Now" jailbreak prompts
- **WildJailbreak**: Real-world jailbreak attempts
- **JailbreakBench**: Systematic jailbreak evaluation

---

## Failed Downloads (1/13)

### HackAPrompt
- **Reason**: Gated dataset requiring HuggingFace authentication
- **Source**: hackaprompt/hackaprompt-dataset (HuggingFace)
- **Tier**: 1 (Must have)
- **Status**: Manual intervention required

**How to Download:**
1. Authenticate with HuggingFace: `huggingface-cli login`
2. Request access at: https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
3. After approval, run:
   ```python
   from datasets import load_dataset
   from pathlib import Path

   output_dir = Path("data/raw_datasets/hackaprompt")
   output_dir.mkdir(parents=True, exist_ok=True)

   dataset = load_dataset("hackaprompt/hackaprompt-dataset")
   for split_name, split_data in dataset.items():
       parquet_path = output_dir / f"{split_name}.parquet"
       split_data.to_parquet(str(parquet_path))
       print(f"Saved {split_name}: {len(split_data)} rows")
   ```

---

## Storage Summary

**Total Storage**: 2.1 GB

**By Source Type:**
- **GitHub repositories**: 8 datasets (1.6 GB)
- **HuggingFace datasets**: 4 datasets (472 MB)

**Breakdown:**
```
data/raw_datasets/
├── alert/              978M
├── harmbench/          469M
├── llmail_inject/      411M
├── wildjailbreak/      101M
├── mosscap/             61M
├── dan_jailbreak/       52M
├── tensortrust/         16M
├── jailbreakbench/     4.0M
├── bipia/              3.5M
├── open_prompt_injection/ 1.8M
├── gandalf_ignore/      64K
└── deepset_injection/   64K
```

---

## Dataset Statistics

### Total Prompts (Estimated)
- **Microsoft LLMail-Inject**: 461,640 prompts
- **Mosscap Prompt Injection**: 278,945 prompts
- **Gandalf Ignore Instructions**: 1,000 prompts
- **deepset prompt-injections**: 662 prompts
- **BIPIA**: 15+ attack categories across multiple domains
- **Other datasets**: Thousands more (exact counts in individual READMEs)

**Estimated Total**: 750,000+ adversarial prompts

### Attack Types Covered
1. **Prompt Injection**
   - Direct injection
   - Indirect injection (BIPIA)
   - Email-based injection (LLMail-Inject)
   - Multi-level injection (Mosscap)

2. **Jailbreak Attacks**
   - DAN (Do Anything Now)
   - Wild/real-world attempts
   - Systematic jailbreak patterns

3. **Instruction Bypass**
   - Ignoring instructions (Gandalf)
   - Role-playing attacks
   - Context manipulation

4. **Adversarial Language**
   - Retrieval task attacks (ALERT)
   - Harm benchmarks (HarmBench)
   - Multi-domain attacks

### Domains Covered
- Email communication
- Code generation
- Table/data processing
- Question answering
- Abstract reasoning
- General conversation
- Retrieval augmented generation

---

## Verification Status

All 12 downloaded datasets have been verified for integrity:

**HuggingFace Datasets:**
- ✓ Parquet files load successfully with pandas
- ✓ Sample data extracted and inspected
- ✓ Column schemas documented

**GitHub Repositories:**
- ✓ Valid git repositories
- ✓ Data files present and accessible
- ✓ File counts documented

**Quality Checks:**
- ✓ No corrupted files
- ✓ All expected splits present
- ✓ Readable formats (JSON, JSONL, Parquet)

---

## Documentation

Each dataset includes comprehensive documentation:

### Individual Dataset READMEs
Each dataset directory contains a README with:
- Source URL and type
- Download date
- Dataset size and statistics
- License information
- Citation information
- File structure
- Usage notes

### Master Manifest
- Location: `data/raw_datasets/MANIFEST.md`
- Contains: Complete inventory, download instructions, research applications

### Download Scripts
- `scripts/download_datasets.py`: Main download script
- `scripts/download_additional_datasets.py`: Supplementary datasets

---

## Next Steps

### Immediate
1. **Download HackAPrompt** (requires authentication)
   - Set up HuggingFace authentication
   - Request dataset access
   - Download using provided script

### Future Additions
2. **Verify existing datasets** mentioned in project:
   - OR-Bench
   - system-prompt-leakage
   - Alignment-Lab prompt injection
   - Check if already in codebase
   - Document sources if found

### Integration
3. **Dataset integration into PromptGuard:**
   - Create unified loading interface
   - Standardize format across datasets
   - Build evaluation pipeline
   - Generate baseline metrics

---

## Research Applications

These datasets enable:

1. **Prompt Injection Detection**
   - Train detection models
   - Benchmark detection accuracy
   - Identify attack patterns

2. **Jailbreak Prevention**
   - Analyze jailbreak techniques
   - Develop defenses
   - Test robustness

3. **Adversarial Robustness**
   - Multi-domain evaluation
   - Cross-dataset generalization
   - Attack taxonomy development

4. **Safety Alignment**
   - Harm classification
   - Risk assessment
   - Safety benchmarking

5. **Red Teaming**
   - LLM security testing
   - Vulnerability discovery
   - Defense validation

---

## License Compliance

Each dataset has its own license. Before use:
- ✓ Check individual dataset READMEs
- ✓ Review source repository licenses
- ✓ Ensure compliance with usage terms
- ✓ Cite original papers when publishing

**Common Licenses:**
- Microsoft datasets: MIT License
- Academic datasets: Varies (check source)
- HuggingFace datasets: See dataset cards

---

## Technical Details

### Download Methods
- **HuggingFace**: Python `datasets` library
- **GitHub**: Git clone with depth=1 (space optimization)
- **Format**: Original formats preserved (no transformations)

### File Formats
- **Parquet**: HuggingFace datasets (efficient, columnar)
- **JSONL**: Many GitHub datasets (line-delimited JSON)
- **JSON**: Some GitHub datasets (single JSON files)
- **CSV**: Occasional format (some repos)

### Storage Optimization
- Git repositories cloned with `--depth 1` (shallow clone)
- Parquet format for HuggingFace (compressed, efficient)
- .gitignore configured to exclude from version control

---

## Troubleshooting

### Common Issues

**Issue**: "Dataset not found" error
- **Solution**: Check dataset ID spelling, verify it exists on HuggingFace

**Issue**: "Authentication required" error
- **Solution**: Run `huggingface-cli login` and authenticate

**Issue**: "Git clone timeout"
- **Solution**: Check internet connection, try again, or increase timeout

**Issue**: "Disk space error"
- **Solution**: Ensure 3+ GB free space before downloading

### Re-downloading Datasets
To re-download a corrupted or incomplete dataset:
```bash
rm -rf data/raw_datasets/[dataset_name]
python scripts/download_datasets.py
```

---

## Credits

### Dataset Authors
- **Microsoft Research**: BIPIA, LLMail-Inject
- **Human Compatible AI**: TensorTrust
- **Lakera AI**: Gandalf, Mosscap
- **Center for AI Safety**: HarmBench
- **Allen Institute for AI**: WildJailbreak
- **Babelscape**: ALERT
- **deepset**: prompt-injections
- **Various researchers**: DAN Jailbreak, JailbreakBench, Open-Prompt-Injection

### Download Infrastructure
- **HuggingFace Hub**: Dataset hosting and API
- **GitHub**: Repository hosting
- **Python libraries**: `datasets`, `pandas`, `git`

---

## Changelog

### 2025-11-04 - Initial Download
- Downloaded 12/13 datasets (2.1 GB total)
- All Tier 2 and Tier 3 datasets acquired
- 4/5 Tier 1 datasets acquired
- HackAPrompt pending authentication
- Created comprehensive documentation
- Verified all dataset integrity
- Added to .gitignore

---

## Contact

For questions about these datasets:
- Refer to individual dataset READMEs
- Check source repositories
- Contact dataset authors (links in MANIFEST.md)

For questions about PromptGuard integration:
- See project documentation
- Check CLAUDE.md for guidance
- Review research questions in docs/

---

**End of Report**
