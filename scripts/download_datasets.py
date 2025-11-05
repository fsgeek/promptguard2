#!/usr/bin/env python
"""
Download adversarial prompt datasets for prompt injection research.
Handles HuggingFace datasets, GitHub repos, and various formats.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import sys

try:
    from datasets import load_dataset
    from huggingface_hub import hf_hub_download, list_repo_files
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("Warning: HuggingFace libraries not available")

BASE_DIR = Path("/home/tony/projects/promptguard/promptguard2/data/raw_datasets")

# Dataset definitions
DATASETS = {
    # TIER 1 (Must have)
    "bipia": {
        "name": "Microsoft BIPIA",
        "source_type": "huggingface",
        "source": "microsoft/BIPIA",
        "github": "https://github.com/microsoft/BIPIA",
        "tier": 1,
    },
    "llmail_inject": {
        "name": "Microsoft LLMail-Inject",
        "source_type": "huggingface",
        "source": "microsoft/llmail-inject-challenge",
        "tier": 1,
    },
    "tensortrust": {
        "name": "TensorTrust",
        "source_type": "github",
        "source": "https://github.com/HumanCompatibleAI/tensor-trust.git",
        "website": "https://tensortrust.ai/paper",
        "tier": 1,
    },
    "hackaprompt": {
        "name": "HackAPrompt",
        "source_type": "huggingface",
        "source": "hackaprompt/hackaprompt-dataset",
        "tier": 1,
    },
    "dan_jailbreak": {
        "name": "DAN Jailbreak",
        "source_type": "github",
        "source": "https://github.com/verazuo/jailbreak_llms.git",
        "tier": 1,
    },

    # TIER 2 (High value)
    "harmbench": {
        "name": "HarmBench",
        "source_type": "github",
        "source": "https://github.com/centerforaisafety/HarmBench.git",
        "website": "https://harmbench.org",
        "tier": 2,
    },
    "wildjailbreak": {
        "name": "WildJailbreak",
        "source_type": "github",
        "source": "https://github.com/allenai/wildteaming.git",
        "tier": 2,
    },
    "gandalf_ignore": {
        "name": "Gandalf Ignore Instructions",
        "source_type": "huggingface",
        "source": "Lakera/gandalf_ignore_instructions",
        "tier": 2,
    },
    "mosscap": {
        "name": "Mosscap Prompt Injection",
        "source_type": "huggingface",
        "source": "Lakera/mosscap_prompt_injection",
        "tier": 2,
    },
    "alert": {
        "name": "ALERT",
        "source_type": "github",
        "source": "https://github.com/Babelscape/ALERT.git",
        "tier": 2,
    },

    # TIER 3 (Supplementary)
    "jailbreakbench": {
        "name": "JailbreakBench",
        "source_type": "github",
        "source": "https://github.com/JailbreakBench/jailbreakbench.git",
        "tier": 3,
    },
    "deepset_injection": {
        "name": "deepset prompt-injections",
        "source_type": "huggingface",
        "source": "deepset/prompt-injections",
        "tier": 3,
    },
    "open_prompt_injection": {
        "name": "Open-Prompt-Injection",
        "source_type": "github",
        "source": "https://github.com/liu00222/Open-Prompt-Injection.git",
        "tier": 3,
    },
}


def download_huggingface_dataset(dataset_id: str, output_dir: Path) -> Tuple[bool, str, Dict]:
    """Download a dataset from HuggingFace."""
    if not HF_AVAILABLE:
        return False, "HuggingFace libraries not available", {}

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"  Downloading {dataset_id} from HuggingFace...")
        dataset = load_dataset(dataset_id, trust_remote_code=True)

        # Save in multiple formats
        stats = {}

        # Save as parquet (most efficient)
        for split_name, split_data in dataset.items():
            parquet_path = output_dir / f"{split_name}.parquet"
            split_data.to_parquet(str(parquet_path))
            stats[split_name] = len(split_data)
            print(f"    Saved {split_name}: {len(split_data)} rows -> {parquet_path.name}")

        # Also save a JSON sample for inspection
        sample_path = output_dir / "sample.json"
        first_split = list(dataset.keys())[0]
        sample_size = min(10, len(dataset[first_split]))
        sample_data = dataset[first_split].select(range(sample_size))
        with open(sample_path, 'w') as f:
            json.dump(sample_data.to_dict(), f, indent=2)

        return True, "Success", stats

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "authentication" in error_msg.lower():
            return False, "Requires HuggingFace authentication", {}
        elif "404" in error_msg or "not found" in error_msg.lower():
            return False, "Dataset not found", {}
        else:
            return False, f"Error: {error_msg}", {}


def download_github_repo(repo_url: str, output_dir: Path) -> Tuple[bool, str, Dict]:
    """Clone a GitHub repository."""
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"  Cloning {repo_url}...")

        # Clone with depth=1 to save space
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(output_dir)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            return False, f"Git clone failed: {result.stderr}", {}

        # Get repo size
        size_result = subprocess.run(
            ["du", "-sh", str(output_dir)],
            capture_output=True,
            text=True
        )
        size = size_result.stdout.split()[0] if size_result.returncode == 0 else "unknown"

        return True, "Success", {"size": size}

    except subprocess.TimeoutExpired:
        return False, "Clone timeout (>5 minutes)", {}
    except Exception as e:
        return False, f"Error: {str(e)}", {}


def get_directory_size(path: Path) -> str:
    """Get human-readable directory size."""
    try:
        result = subprocess.run(
            ["du", "-sh", str(path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.split()[0]
    except:
        pass
    return "unknown"


def verify_dataset(output_dir: Path, source_type: str) -> Tuple[bool, str]:
    """Verify a downloaded dataset can be read."""
    try:
        if source_type == "huggingface":
            # Check for parquet files
            parquet_files = list(output_dir.glob("*.parquet"))
            if not parquet_files:
                return False, "No parquet files found"

            # Try to read first file
            import pandas as pd
            df = pd.read_parquet(parquet_files[0])
            rows = len(df)
            return True, f"Verified: {rows} rows in {parquet_files[0].name}"

        elif source_type == "github":
            # Check if .git directory exists
            if not (output_dir / ".git").exists():
                return False, "Not a valid git repository"

            # Count data files
            data_files = (
                list(output_dir.glob("**/*.json")) +
                list(output_dir.glob("**/*.csv")) +
                list(output_dir.glob("**/*.parquet")) +
                list(output_dir.glob("**/*.jsonl"))
            )
            # Filter out files in .git directory
            data_files = [f for f in data_files if ".git" not in str(f)]

            return True, f"Verified: {len(data_files)} data files found"

    except Exception as e:
        return False, f"Verification failed: {str(e)}"


def create_readme(output_dir: Path, dataset_info: Dict, download_stats: Dict, download_date: str):
    """Create README.md for a dataset."""
    readme_path = output_dir / "README.md"

    content = f"""# {dataset_info['name']}

## Source
- **Type**: {dataset_info['source_type']}
- **Source**: {dataset_info['source']}
"""

    if 'github' in dataset_info:
        content += f"- **GitHub**: {dataset_info['github']}\n"
    if 'website' in dataset_info:
        content += f"- **Website**: {dataset_info['website']}\n"

    content += f"""
## Download Information
- **Downloaded**: {download_date}
- **Size**: {get_directory_size(output_dir)}
- **Tier**: {dataset_info['tier']}

## Dataset Statistics
"""

    if download_stats:
        content += "```json\n"
        content += json.dumps(download_stats, indent=2)
        content += "\n```\n"

    content += """
## License
Please refer to the source repository for license information.

## Citation
Please refer to the source repository for citation information.

## Notes
- Original format preserved
- No transformations applied
- Downloaded for PromptGuard research
"""

    with open(readme_path, 'w') as f:
        f.write(content)


def main():
    """Main download orchestration."""
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("ADVERSARIAL PROMPT DATASET DOWNLOADER")
    print("=" * 80)
    print()

    results = {
        "successful": [],
        "failed": [],
        "download_date": datetime.now().isoformat()
    }

    # Sort by tier
    sorted_datasets = sorted(DATASETS.items(), key=lambda x: x[1]['tier'])

    for dataset_id, dataset_info in sorted_datasets:
        print(f"\n[Tier {dataset_info['tier']}] {dataset_info['name']}")
        print("-" * 80)

        output_dir = BASE_DIR / dataset_id

        # Skip if already exists
        if output_dir.exists() and any(output_dir.iterdir()):
            print(f"  ⚠️  Directory already exists: {output_dir}")
            print(f"  Skipping download. Delete directory to re-download.")

            # Still verify
            is_valid, verify_msg = verify_dataset(output_dir, dataset_info['source_type'])
            if is_valid:
                size = get_directory_size(output_dir)
                results["successful"].append({
                    "id": dataset_id,
                    "name": dataset_info['name'],
                    "size": size,
                    "note": "Already existed"
                })
            else:
                results["failed"].append({
                    "id": dataset_id,
                    "name": dataset_info['name'],
                    "reason": f"Exists but verification failed: {verify_msg}"
                })
            continue

        # Download based on source type
        if dataset_info['source_type'] == 'huggingface':
            success, message, stats = download_huggingface_dataset(
                dataset_info['source'], output_dir
            )
        elif dataset_info['source_type'] == 'github':
            success, message, stats = download_github_repo(
                dataset_info['source'], output_dir
            )
        else:
            success = False
            message = "Unknown source type"
            stats = {}

        if success:
            print(f"  ✓ {message}")

            # Create README
            create_readme(output_dir, dataset_info, stats, results['download_date'])

            # Verify
            is_valid, verify_msg = verify_dataset(output_dir, dataset_info['source_type'])
            if is_valid:
                print(f"  ✓ {verify_msg}")
                size = get_directory_size(output_dir)
                results["successful"].append({
                    "id": dataset_id,
                    "name": dataset_info['name'],
                    "size": size,
                    "source": dataset_info['source']
                })
            else:
                print(f"  ✗ {verify_msg}")
                results["failed"].append({
                    "id": dataset_id,
                    "name": dataset_info['name'],
                    "reason": f"Download succeeded but verification failed: {verify_msg}"
                })
        else:
            print(f"  ✗ {message}")
            results["failed"].append({
                "id": dataset_id,
                "name": dataset_info['name'],
                "reason": message
            })

    # Create manifest
    create_manifest(results)

    # Print summary
    print_summary(results)


def create_manifest(results: Dict):
    """Create MANIFEST.md with download results."""
    manifest_path = BASE_DIR / "MANIFEST.md"

    content = f"""# Dataset Download Manifest

**Generated**: {results['download_date']}

## Summary
- **Successful**: {len(results['successful'])}/{len(DATASETS)}
- **Failed**: {len(results['failed'])}/{len(DATASETS)}

## Successfully Downloaded

| ID | Name | Size | Source |
|----|------|------|--------|
"""

    for item in results['successful']:
        source = item.get('source', 'N/A')
        content += f"| `{item['id']}` | {item['name']} | {item['size']} | {source} |\n"

    if results['failed']:
        content += "\n## Failed Downloads\n\n"
        for item in results['failed']:
            content += f"### {item['name']} (`{item['id']}`)\n"
            content += f"**Reason**: {item['reason']}\n\n"

    content += """
## Storage Location
```
data/raw_datasets/
├── bipia/
├── llmail_inject/
├── tensortrust/
└── ... (one directory per dataset)
```

## Usage Notes
- All datasets are in their original format
- See individual README.md files for details
- Datasets are gitignored (not committed to repo)
- For authentication-required datasets, set up HuggingFace CLI

## Authentication Setup (if needed)
```bash
huggingface-cli login
```

## Verification
Each dataset has been verified for integrity:
- HuggingFace datasets: Can load parquet files
- GitHub repos: Valid git repository with data files
"""

    with open(manifest_path, 'w') as f:
        f.write(content)

    print(f"\n📄 Manifest created: {manifest_path}")


def print_summary(results: Dict):
    """Print summary report."""
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)

    print(f"\n✓ Successfully Downloaded: {len(results['successful'])}/{len(DATASETS)}")
    for item in results['successful']:
        print(f"  - {item['name']} ({item['size']})")

    if results['failed']:
        print(f"\n✗ Failed Downloads: {len(results['failed'])}/{len(DATASETS)}")
        for item in results['failed']:
            print(f"  - {item['name']}: {item['reason']}")

    # Calculate total size
    total_size_cmd = subprocess.run(
        ["du", "-sh", str(BASE_DIR)],
        capture_output=True,
        text=True
    )
    if total_size_cmd.returncode == 0:
        total_size = total_size_cmd.stdout.split()[0]
        print(f"\n📊 Total Storage: {total_size}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
