#!/usr/bin/env python
"""
Download additional datasets that failed in initial download.
Tries alternative sources and methods.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/tony/projects/promptguard/promptguard2/data/raw_datasets")

def download_bipia_from_github():
    """Try to download BIPIA from GitHub releases or data directory."""
    output_dir = BASE_DIR / "bipia"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Attempting to download Microsoft BIPIA from GitHub...")

    # Try cloning the repo
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/microsoft/BIPIA.git", str(output_dir)],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("✓ Successfully cloned BIPIA repository")
            return True
        else:
            print(f"✗ Failed to clone: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def download_hackaprompt_alternative():
    """Try alternative sources for HackAPrompt dataset."""
    output_dir = BASE_DIR / "hackaprompt"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Attempting to download HackAPrompt from alternative sources...")

    # Try to download from direct URLs if available
    # The dataset might be available on GitHub or other repositories

    # First, try cloning any associated GitHub repos
    github_urls = [
        "https://github.com/prompt-security/hackaprompt.git",
        "https://github.com/HackAPrompt/hackaprompt.git",
    ]

    for url in github_urls:
        try:
            print(f"  Trying {url}...")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", url, str(output_dir)],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print(f"✓ Successfully cloned from {url}")
                return True

        except Exception as e:
            print(f"  Failed: {str(e)}")
            continue

    print("✗ No alternative sources worked for HackAPrompt")
    print("  This dataset requires HuggingFace authentication.")
    print("  Run: huggingface-cli login")
    return False


def main():
    print("=" * 80)
    print("DOWNLOADING ADDITIONAL DATASETS")
    print("=" * 80)
    print()

    results = []

    # Try BIPIA
    print("\n[1/2] Microsoft BIPIA")
    print("-" * 80)
    success = download_bipia_from_github()
    results.append(("BIPIA", success))

    # Try HackAPrompt
    print("\n[2/2] HackAPrompt")
    print("-" * 80)
    success = download_hackaprompt_alternative()
    results.append(("HackAPrompt", success))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    successful = [name for name, success in results if success]
    failed = [name for name, success in results if not success]

    if successful:
        print(f"\n✓ Successfully downloaded: {len(successful)}")
        for name in successful:
            print(f"  - {name}")

    if failed:
        print(f"\n✗ Still failed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
