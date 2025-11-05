import argparse
import json
import os
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd
from arango.collection import StandardCollection
from pydantic import ValidationError

from src.database.client import get_client
from src.database.schemas.adversarial_prompts import AdversarialPrompt


def process_bipia_batch(records: List[Dict[str, Any]], normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    for record in records:
        raw_key = str(uuid.uuid4())
        raw_record = record.copy()
        raw_record['_key'] = raw_key
        raw_records_to_insert.append(raw_record)

        try:
            context = record.get("context", "")
            prompt_text = "\n".join(context) if isinstance(context, list) else context

            ideal = record.get("ideal")
            expected_output_text = "\n".join(ideal) if isinstance(ideal, list) else ideal

            split = "train" if "train" in source_file.name else "test"
            domain = source_file.parent.name

            normalized_key = str(uuid.uuid4())
            normalized_prompt = AdversarialPrompt(
                source_dataset="bipia",
                source_file=str(source_file.relative_to(dataset_path)),
                split=split,
                attack_type="prompt_injection",
                domain=domain,
                prompt=prompt_text,
                user_task=record.get("question"),
                expected_output=expected_output_text,
                is_adversarial=True,
                raw_record_link=f"{raw_collection.name}/{raw_key}"
            )
            
            normalized_dict = normalized_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count

def ingest_bipia_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):
    """Ingest data from the BIPIA dataset."""
    print(f"Ingesting BIPIA dataset from {dataset_path}")
    
    success_count = 0
    failure_count = 0
    BATCH_SIZE = 1000
    
    benchmark_path = dataset_path / "benchmark"
    
    # Process .json files (e.g., text_attack_train.json)
    for json_file in benchmark_path.glob("*.json"):
        print(f"Processing JSON file: {json_file.name}")
        records_batch = []
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for category, prompts in data.items():
                for prompt_text in prompts:
                    records_batch.append({"category": category, "prompt": prompt_text})
                    if len(records_batch) >= BATCH_SIZE:
                        success_count, failure_count = process_bipia_json_batch(records_batch, normalized_collection, raw_collection, edge_collection, json_file, dataset_path, success_count, failure_count)
                        records_batch = []
            if records_batch:
                success_count, failure_count = process_bipia_json_batch(records_batch, normalized_collection, raw_collection, edge_collection, json_file, dataset_path, success_count, failure_count)
        except Exception as e:
            print(f"Error processing file {json_file.name}: {e}")

    # Process .jsonl files (e.g., email/train.jsonl)
    for jsonl_file in benchmark_path.glob("**/*.jsonl"):
        print(f"Processing JSONL file: {jsonl_file.name}")
        records_batch = []
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    records_batch.append(json.loads(line))
                    if len(records_batch) >= BATCH_SIZE:
                        success_count, failure_count = process_bipia_batch(records_batch, normalized_collection, raw_collection, edge_collection, jsonl_file, dataset_path, success_count, failure_count)
                        records_batch = []
                if records_batch:
                    success_count, failure_count = process_bipia_batch(records_batch, normalized_collection, raw_collection, edge_collection, jsonl_file, dataset_path, success_count, failure_count)
        except Exception as e:
            print(f"Error processing file {jsonl_file.name}: {e}")

    print(f"Finished ingesting BIPIA dataset.")
    print(f"Summary: {success_count} successful, {failure_count} failed.")

def process_bipia_json_batch(records: List[Dict[str, Any]], normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    for record in records:
        raw_key = str(uuid.uuid4())
        raw_record = record.copy()
        raw_record['_key'] = raw_key
        raw_records_to_insert.append(raw_record)

        try:
            split = "train" if "train" in source_file.name else "test"
            domain = source_file.stem.split('_')[0]

            normalized_key = str(uuid.uuid4())
            adversarial_prompt = AdversarialPrompt(
                source_dataset="bipia",
                source_file=str(source_file.relative_to(dataset_path)),
                split=split,
                attack_type="prompt_injection",
                domain=domain,
                prompt=record.get("prompt", ""),
                user_task=record.get("category"),
                is_adversarial=True,
                raw_record_link=f"{raw_collection.name}/{raw_key}"
            )
            
            normalized_dict = adversarial_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count



def process_llmail_batch(df_batch: pd.DataFrame, normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    split = source_file.stem
    for _, record in df_batch.iterrows():
        record_dict = record.to_dict()
        raw_key = str(uuid.uuid4())
        record_dict['_key'] = raw_key
        raw_records_to_insert.append(record_dict)

        try:
            attack_objectives = None
            if "objectives" in record_dict and isinstance(record_dict["objectives"], str):
                try:
                    attack_objectives = json.loads(record_dict["objectives"])
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode objectives JSON for {record_dict.get('RowKey')}")

            normalized_key = str(uuid.uuid4())
            adversarial_prompt = AdversarialPrompt(
                source_dataset="llmail_inject",
                source_file=str(source_file.relative_to(dataset_path)),
                raw_record_id=record_dict.get("RowKey"),
                split=split,
                attack_type="prompt_injection",
                domain="email",
                prompt=record_dict.get("body", ""),
                attack_objectives=attack_objectives,
                is_adversarial=True,
                raw_record_link=f"{raw_collection.name}/{raw_key}"
            )
            
            normalized_dict = adversarial_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record_dict}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count

def ingest_llmail_inject_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):
    """Ingest data from the LLMail-Inject dataset."""
    print(f"Ingesting LLMail-Inject dataset from {dataset_path}")
    
    success_count = 0
    failure_count = 0
    BATCH_SIZE = 1000

    for parquet_file in dataset_path.glob("*.parquet"):
        print(f"Processing Parquet file: {parquet_file.name}")
        try:
            df = pd.read_parquet(parquet_file)
            for i in range(0, len(df), BATCH_SIZE):
                df_batch = df.iloc[i:i + BATCH_SIZE]
                success_count, failure_count = process_llmail_batch(df_batch, normalized_collection, raw_collection, edge_collection, parquet_file, dataset_path, success_count, failure_count)
        except Exception as e:
            print(f"Error processing file {parquet_file.name}: {e}")

    print(f"Finished ingesting LLMail-Inject dataset.")
    print(f"Summary: {success_count} successful, {failure_count} failed.")


def process_tensortrust_batch(df_batch: pd.DataFrame, normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int, is_attack: bool):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    for _, record in df_batch.iterrows():
        record_dict = record.to_dict()
        raw_key = str(uuid.uuid4())
        record_dict['_key'] = raw_key
        raw_records_to_insert.append(record_dict)

        try:
            normalized_key = str(uuid.uuid4())
            if is_attack:
                prompt_text = record_dict.get("prompt", record_dict.get("attack_prompt", ""))
                adversarial_prompt = AdversarialPrompt(
                    source_dataset="tensortrust",
                    source_file=str(source_file.relative_to(dataset_path)),
                    attack_type="red_teaming",
                    domain="game",
                    prompt=prompt_text,
                    is_adversarial=True,
                    raw_record_link=f"{raw_collection.name}/{raw_key}"
                )
            else: # is_defense
                pre_prompt = record_dict.get("pre_prompt", "")
                post_prompt = record_dict.get("post_prompt", "")
                full_prompt = pre_prompt + " " + post_prompt
                adversarial_prompt = AdversarialPrompt(
                    source_dataset="tensortrust",
                    source_file=str(source_file.relative_to(dataset_path)),
                    attack_type="defense",
                    domain="game",
                    prompt=full_prompt.strip(),
                    prompt_components={
                        "pre_prompt": pre_prompt,
                        "post_prompt": post_prompt,
                        "access_code": record_dict.get("access_code")
                    },
                    is_adversarial=False,
                    raw_record_link=f"{raw_collection.name}/{raw_key}"
                )
            
            normalized_dict = adversarial_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record_dict}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count

def ingest_tensortrust_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):
    """Ingest data from the TensorTrust dataset."""
    print(f"Ingesting TensorTrust dataset from {dataset_path}")
    
    success_count = 0
    failure_count = 0
    BATCH_SIZE = 1000
    data_dir = dataset_path / "data"

    # Process annotated_attacks.parquet
    attacks_file = data_dir / "annotated_attacks.parquet"
    if attacks_file.exists():
        print(f"Processing attacks file: {attacks_file.name}")
        try:
            df_attacks = pd.read_parquet(attacks_file)
            for i in range(0, len(df_attacks), BATCH_SIZE):
                df_batch = df_attacks.iloc[i:i + BATCH_SIZE]
                success_count, failure_count = process_tensortrust_batch(df_batch, normalized_collection, raw_collection, edge_collection, attacks_file, dataset_path, success_count, failure_count, is_attack=True)
        except Exception as e:
            print(f"Error processing file {attacks_file.name}: {e}")
    else:
        print(f"Attacks file not found: {attacks_file}")

    # Process gameui_defense.parquet
    defenses_file = data_dir / "gameui_defense.parquet"
    if defenses_file.exists():
        print(f"Processing defenses file: {defenses_file.name}")
        try:
            df_defenses = pd.read_parquet(defenses_file)
            for i in range(0, len(df_defenses), BATCH_SIZE):
                df_batch = df_defenses.iloc[i:i + BATCH_SIZE]
                success_count, failure_count = process_tensortrust_batch(df_batch, normalized_collection, raw_collection, edge_collection, defenses_file, dataset_path, success_count, failure_count, is_attack=False)
        except Exception as e:
            print(f"Error processing file {defenses_file.name}: {e}")
    else:
        print(f"Defenses file not found: {defenses_file}")

    print(f"Finished ingesting TensorTrust dataset.")
    print(f"Summary: {success_count} successful, {failure_count} failed.")


def process_gandalf_batch(df_batch: pd.DataFrame, normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    split = source_file.stem
    for _, record in df_batch.iterrows():
        record_dict = record.to_dict()
        raw_key = str(uuid.uuid4())
        record_dict['_key'] = raw_key
        raw_records_to_insert.append(record_dict)

        try:
            normalized_key = str(uuid.uuid4())
            adversarial_prompt = AdversarialPrompt(
                source_dataset="gandalf_ignore",
                source_file=str(source_file.relative_to(dataset_path)),
                split=split,
                attack_type="ignore_instruction",
                domain="general",
                prompt=record_dict.get("text", ""),
                is_adversarial=True,
                raw_record_link=f"{raw_collection.name}/{raw_key}"
            )
            
            normalized_dict = adversarial_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record_dict}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count

def ingest_gandalf_ignore_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):
    """Ingest data from the Gandalf Ignore dataset."""
    print(f"Ingesting Gandalf Ignore dataset from {dataset_path}")
    
    success_count = 0
    failure_count = 0
    BATCH_SIZE = 1000

    for parquet_file in dataset_path.glob("*.parquet"):
        print(f"Processing Parquet file: {parquet_file.name}")
        try:
            df = pd.read_parquet(parquet_file)
            for i in range(0, len(df), BATCH_SIZE):
                df_batch = df.iloc[i:i + BATCH_SIZE]
                success_count, failure_count = process_gandalf_batch(df_batch, normalized_collection, raw_collection, edge_collection, parquet_file, dataset_path, success_count, failure_count)
        except Exception as e:
            print(f"Error processing file {parquet_file.name}: {e}")

    print(f"Finished ingesting Gandalf Ignore dataset.")
    print(f"Summary: {success_count} successful, {failure_count} failed.")

def process_mosscap_batch(df_batch: pd.DataFrame, normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    split = source_file.stem
    for _, record in df_batch.iterrows():
        record_dict = record.to_dict()
        raw_key = str(uuid.uuid4())
        record_dict['_key'] = raw_key
        raw_records_to_insert.append(record_dict)

        try:
            normalized_key = str(uuid.uuid4())
            adversarial_prompt = AdversarialPrompt(
                source_dataset="mosscap",
                source_file=str(source_file.relative_to(dataset_path)),
                split=split,
                attack_type="prompt_injection",
                domain="general",
                prompt=record_dict.get("prompt", ""),
                expected_output=record_dict.get("answer"),
                is_adversarial=True,
                raw_record_link=f"{raw_collection.name}/{raw_key}"
            )
            
            normalized_dict = adversarial_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record_dict}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count

def ingest_mosscap_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):
    """Ingest data from the Mosscap dataset."""
    print(f"Ingesting Mosscap dataset from {dataset_path}")
    
    success_count = 0
    failure_count = 0
    BATCH_SIZE = 1000

    for parquet_file in dataset_path.glob("*.parquet"):
        print(f"Processing Parquet file: {parquet_file.name}")
        try:
            df = pd.read_parquet(parquet_file)
            for i in range(0, len(df), BATCH_SIZE):
                df_batch = df.iloc[i:i + BATCH_SIZE]
                success_count, failure_count = process_mosscap_batch(df_batch, normalized_collection, raw_collection, edge_collection, parquet_file, dataset_path, success_count, failure_count)
        except Exception as e:
            print(f"Error processing file {parquet_file.name}: {e}")

    print(f"Finished ingesting Mosscap dataset.")
    print(f"Summary: {success_count} successful, {failure_count} failed.")

def process_deepset_batch(df_batch: pd.DataFrame, normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    split = source_file.stem
    for _, record in df_batch.iterrows():
        record_dict = record.to_dict()
        raw_key = str(uuid.uuid4())
        record_dict['_key'] = raw_key
        raw_records_to_insert.append(record_dict)

        try:
            normalized_key = str(uuid.uuid4())
            adversarial_prompt = AdversarialPrompt(
                source_dataset="deepset_injection",
                source_file=str(source_file.relative_to(dataset_path)),
                split=split,
                attack_type="prompt_injection",
                domain="general",
                prompt=record_dict.get("text", ""),
                is_adversarial=bool(record_dict.get("label")),
                raw_record_link=f"{raw_collection.name}/{raw_key}"
            )
            
            normalized_dict = adversarial_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record_dict}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count

def ingest_deepset_injection_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):
    """Ingest data from the deepset-injection dataset."""
    print(f"Ingesting deepset-injection dataset from {dataset_path}")
    
    success_count = 0
    failure_count = 0
    BATCH_SIZE = 1000

    for parquet_file in dataset_path.glob("*.parquet"):
        print(f"Processing Parquet file: {parquet_file.name}")
        try:
            df = pd.read_parquet(parquet_file)
            for i in range(0, len(df), BATCH_SIZE):
                df_batch = df.iloc[i:i + BATCH_SIZE]
                success_count, failure_count = process_deepset_batch(df_batch, normalized_collection, raw_collection, edge_collection, parquet_file, dataset_path, success_count, failure_count)
        except Exception as e:
            print(f"Error processing file {parquet_file.name}: {e}")

    print(f"Finished ingesting deepset-injection dataset.")
    print(f"Summary: {success_count} successful, {failure_count} failed.")

def ingest_dan_jailbreak_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):
    """Ingest data from the DAN Jailbreak dataset."""
    print(f"Ingesting DAN Jailbreak dataset from {dataset_path}")
    
    success_count = 0
    failure_count = 0
    BATCH_SIZE = 1000
    
    prompts_path = dataset_path / "data" / "prompts"

    for csv_file in prompts_path.glob("*.csv"):
        print(f"Processing CSV file: {csv_file.name}")
        try:
            df = pd.read_csv(csv_file)
            # Replace NaN with None to avoid ArangoDB VPack errors
            df = df.replace({np.nan: None})
            for i in range(0, len(df), BATCH_SIZE):
                df_batch = df.iloc[i:i + BATCH_SIZE]
                success_count, failure_count = process_dan_jailbreak_batch(df_batch, normalized_collection, raw_collection, edge_collection, csv_file, dataset_path, success_count, failure_count)
        except Exception as e:
            print(f"Error processing file {csv_file.name}: {e}")

    print(f"Finished ingesting DAN Jailbreak dataset.")
    print(f"Summary: {success_count} successful, {failure_count} failed.")

def process_dan_jailbreak_batch(df_batch: pd.DataFrame, normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    for _, record in df_batch.iterrows():
        record_dict = record.to_dict()
        raw_key = str(uuid.uuid4())
        record_dict['_key'] = raw_key
        raw_records_to_insert.append(record_dict)

        try:
            # Extract date from filename like 'jailbreak_prompts_2023_05_07.csv'
            split_date = '_'.join(source_file.stem.split('_')[-3:])

            normalized_key = str(uuid.uuid4())
            adversarial_prompt = AdversarialPrompt(
                source_dataset="dan_jailbreak",
                source_file=str(source_file.relative_to(dataset_path)),
                split=split_date,
                attack_type="jailbreak",
                domain=record_dict.get("platform"),
                prompt=record_dict.get("prompt", ""),
                is_adversarial=bool(record_dict.get("jailbreak")),
                raw_record_link=f"{raw_collection.name}/{raw_key}"
            )
            
            normalized_dict = adversarial_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record_dict}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count

def ingest_harmbench_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):
    """Ingest data from the HarmBench dataset."""
    print(f"Ingesting HarmBench dataset from {dataset_path}")
    
    success_count = 0
    failure_count = 0
    BATCH_SIZE = 1000
    
    behavior_path = dataset_path / "data" / "behavior_datasets"

    for csv_file in behavior_path.glob("harmbench_behaviors_text_*.csv"):
        print(f"Processing CSV file: {csv_file.name}")
        try:
            df = pd.read_csv(csv_file)
            df = df.replace({np.nan: None})
            for i in range(0, len(df), BATCH_SIZE):
                df_batch = df.iloc[i:i + BATCH_SIZE]
                success_count, failure_count = process_harmbench_batch(df_batch, normalized_collection, raw_collection, edge_collection, csv_file, dataset_path, success_count, failure_count)
        except Exception as e:
            print(f"Error processing file {csv_file.name}: {e}")

    print(f"Finished ingesting HarmBench dataset.")
    print(f"Summary: {success_count} successful, {failure_count} failed.")

def process_harmbench_batch(df_batch: pd.DataFrame, normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    for _, record in df_batch.iterrows():
        record_dict = record.to_dict()
        raw_key = str(uuid.uuid4())
        record_dict['_key'] = raw_key
        raw_records_to_insert.append(record_dict)

        try:
            # Extract split from filename like 'harmbench_behaviors_text_all.csv'
            split = source_file.stem.split('_')[-1]

            tags = [record_dict.get("FunctionalCategory")]
            if record_dict.get("Tags"):
                tags.extend(record_dict.get("Tags").split(','))

            normalized_key = str(uuid.uuid4())
            adversarial_prompt = AdversarialPrompt(
                source_dataset="harmbench",
                source_file=str(source_file.relative_to(dataset_path)),
                raw_record_id=record_dict.get("BehaviorID"),
                split=split,
                attack_type="harmful_behavior",
                domain=record_dict.get("SemanticCategory"),
                prompt=record_dict.get("Behavior"),
                prompt_context=record_dict.get("ContextString"),
                tags=tags,
                is_adversarial=True,
                raw_record_link=f"{raw_collection.name}/{raw_key}"
            )
            
            normalized_dict = adversarial_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record_dict}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count



def process_open_prompt_injection_batch(records: List[Dict[str, Any]], normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int):
    raw_records_to_insert = []
    normalized_prompts_to_insert = []
    edges_to_insert = []

    for record in records:
        raw_key = str(uuid.uuid4())
        raw_record = record.copy()
        raw_record['_key'] = raw_key
        raw_records_to_insert.append(raw_record)

        try:
            filename = source_file.name
            parts = filename.replace(".txt", "").split("_")
            
            task = parts[0]
            
            # Determine type and length
            type_parts = []
            length = None
            for part in parts[1:]:
                if part in ["cot", "inject"]: # Known types
                    type_parts.append(part)
                elif part in ["long", "med", "med-long", "short"]: # Known lengths
                    length = part
                elif part == "med-long":
                    length = "med_long"
                else: # Assume it's part of the type if not a known length
                    type_parts.append(part)
            
            prompt_type = "_".join(type_parts)
            if not prompt_type: # Handle cases like 'mathematical_reasoning.txt' with no specific type part
                prompt_type = "default"
            
            is_adversarial = "inject" in prompt_type

            tags = [prompt_type]
            if length:
                tags.append(length)

            normalized_key = str(uuid.uuid4())
            adversarial_prompt = AdversarialPrompt(
                source_dataset="open_prompt_injection",
                source_file=str(source_file.relative_to(dataset_path)),
                split="N/A", # No explicit split in this dataset
                attack_type="prompt_injection" if is_adversarial else "system_prompt",
                domain=task,
                prompt=record.get("prompt_content", ""),
                tags=tags,
                is_adversarial=is_adversarial,
                raw_record_link=f"{raw_collection.name}/{raw_key}"
            )
            
            normalized_dict = adversarial_prompt.model_dump()
            normalized_dict['_key'] = normalized_key
            normalized_prompts_to_insert.append(normalized_dict)

            edges_to_insert.append({
                "_from": f"{normalized_collection.name}/{normalized_key}",
                "_to": f"{raw_collection.name}/{raw_key}"
            })
        except ValidationError as e:
            failure_count += 1
            print(f"--- VALIDATION FAILURE ---")
            print(f"File: {source_file.name}")
            print(f"Record: {record}")
            print(f"Error: {e}")
            print(f"--------------------------")

    if raw_records_to_insert:
        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')
        success_count += raw_results['created']
        failure_count += raw_results['errors']
    
    if normalized_prompts_to_insert:
        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')
        failure_count += norm_results['errors']

    if edges_to_insert:
        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')
        failure_count += edge_results['errors']

    return success_count, failure_count


def ingest_open_prompt_injection_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):


    """Ingest data from the Open Prompt Injection dataset."""


    print(f"Ingesting Open Prompt Injection dataset from {dataset_path}")


    


    success_count = 0


    failure_count = 0


    BATCH_SIZE = 1000


    


    system_prompts_path = dataset_path / "data" / "system_prompts"





    for txt_file in system_prompts_path.glob("*.txt"):


        print(f"Processing TXT file: {txt_file.name}")


        records_batch = []


        try:


            with open(txt_file, 'r', encoding='utf-8') as f:


                prompt_content = f.read().strip()


            


            records_batch.append({"filename": txt_file.name, "prompt_content": prompt_content})


            


            if records_batch: # Process batch even if it's just one record


                success_count, failure_count = process_open_prompt_injection_batch(records_batch, normalized_collection, raw_collection, edge_collection, txt_file, dataset_path, success_count, failure_count)


                records_batch = [] # Clear batch after processing


        except Exception as e:


            print(f"Error processing file {txt_file.name}: {e}")





    print(f"Finished ingesting Open Prompt Injection dataset.")


    print(f"Summary: {success_count} successful, {failure_count} failed.")





def process_alert_batch(records: List[Dict[str, Any]], normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, source_file: Path, dataset_path: Path, success_count: int, failure_count: int, is_adversarial: bool):


    raw_records_to_insert = []


    normalized_prompts_to_insert = []


    edges_to_insert = []





    for record in records:


        raw_key = str(uuid.uuid4())


        raw_record = record.copy()


        raw_record['_key'] = raw_key


        raw_records_to_insert.append(raw_record)





        try:


            normalized_key = str(uuid.uuid4())


            adversarial_prompt = AdversarialPrompt(


                source_dataset="alert",


                source_file=str(source_file.relative_to(dataset_path)),


                raw_record_id=str(record.get("id")),


                attack_type=record.get("attack_type", "harmful_prompt"),


                domain=record.get("category"),


                prompt=record.get("prompt"),


                is_adversarial=is_adversarial,


                raw_record_link=f"{raw_collection.name}/{raw_key}"


            )


            


            normalized_dict = adversarial_prompt.model_dump()


            normalized_dict['_key'] = normalized_key


            normalized_prompts_to_insert.append(normalized_dict)





            edges_to_insert.append({


                "_from": f"{normalized_collection.name}/{normalized_key}",


                "_to": f"{raw_collection.name}/{raw_key}"


            })


        except ValidationError as e:


            failure_count += 1


            print(f"--- VALIDATION FAILURE ---")


            print(f"File: {source_file.name}")


            print(f"Record: {record}")


            print(f"Error: {e}")


            print(f"--------------------------")





    if raw_records_to_insert:


        raw_results = raw_collection.import_bulk(raw_records_to_insert, on_duplicate='ignore')


        success_count += raw_results['created']


        failure_count += raw_results['errors']


    


    if normalized_prompts_to_insert:


        norm_results = normalized_collection.import_bulk(normalized_prompts_to_insert, on_duplicate='ignore')


        failure_count += norm_results['errors']





    if edges_to_insert:


        edge_results = edge_collection.import_bulk(edges_to_insert, on_duplicate='ignore')


        failure_count += edge_results['errors']





    return success_count, failure_count





def ingest_alert_dataset(normalized_collection: StandardCollection, raw_collection: StandardCollection, edge_collection: StandardCollection, dataset_path: Path):


    """Ingest data from the ALERT dataset."""


    print(f"Ingesting ALERT dataset from {dataset_path}")


    


    success_count = 0


    failure_count = 0


    BATCH_SIZE = 1000


    data_dir = dataset_path / "data"





    # Process alert.jsonl (non-adversarial)


    non_adv_file = data_dir / "alert.jsonl"


    if non_adv_file.exists():


        print(f"Processing non-adversarial file: {non_adv_file.name}")


        records_batch = []


        try:


            with open(non_adv_file, 'r', encoding='utf-8') as f:


                for line in f:


                    records_batch.append(json.loads(line))


                    if len(records_batch) >= BATCH_SIZE:


                        success_count, failure_count = process_alert_batch(records_batch, normalized_collection, raw_collection, edge_collection, non_adv_file, dataset_path, success_count, failure_count, is_adversarial=False)


                        records_batch = []


                if records_batch:


                    success_count, failure_count = process_alert_batch(records_batch, normalized_collection, raw_collection, edge_collection, non_adv_file, dataset_path, success_count, failure_count, is_adversarial=False)


        except Exception as e:


            print(f"Error processing file {non_adv_file.name}: {e}")


    else:


        print(f"Non-adversarial file not found: {non_adv_file}")





    # Process alert_adversarial.jsonl (adversarial)


    adv_file = data_dir / "alert_adversarial.jsonl"


    if adv_file.exists():


        print(f"Processing adversarial file: {adv_file.name}")


        records_batch = []


        try:


            with open(adv_file, 'r', encoding='utf-8') as f:


                for line in f:


                    records_batch.append(json.loads(line))


                    if len(records_batch) >= BATCH_SIZE:


                        success_count, failure_count = process_alert_batch(records_batch, normalized_collection, raw_collection, edge_collection, adv_file, dataset_path, success_count, failure_count, is_adversarial=True)


                        records_batch = []


                if records_batch:


                    success_count, failure_count = process_alert_batch(records_batch, normalized_collection, raw_collection, edge_collection, adv_file, dataset_path, success_count, failure_count, is_adversarial=True)


        except Exception as e:


            print(f"Error processing file {adv_file.name}: {e}")


    else:


        print(f"Adversarial file not found: {adv_file}")





    print(f"Finished ingesting ALERT dataset.")


    print(f"Summary: {success_count} successful, {failure_count} failed.")











def main():











    parser = argparse.ArgumentParser(description="Ingest various adversarial prompt datasets into ArangoDB.")











    parser.add_argument("dataset", type=str, help="The name of the dataset to ingest (e.g., 'bipia', 'llmail_inject', 'tensortrust').")











    parser.add_argument("--data_dir", type=str, default="data/raw_datasets", help="Path to the raw datasets directory.")























    args = parser.parse_args()























    client = get_client()











    normalized_collection = client.get_adversarial_prompts_collection()











    raw_collection = client.get_raw_dataset_collection(args.dataset)











    edge_collection = client.get_edge_collection("normalized_from_raw")























    dataset_path = Path(args.data_dir) / args.dataset











    if not dataset_path.exists():











        print(f"Error: Dataset path {dataset_path} does not exist.")











        return























    ingestion_functions = {











        "bipia": ingest_bipia_dataset,











        "llmail_inject": ingest_llmail_inject_dataset,











        "tensortrust": ingest_tensortrust_dataset,











        "gandalf_ignore": ingest_gandalf_ignore_dataset,











        "mosscap": ingest_mosscap_dataset,











        "deepset_injection": ingest_deepset_injection_dataset,











        "dan_jailbreak": ingest_dan_jailbreak_dataset,











        "harmbench": ingest_harmbench_dataset,











        "open_prompt_injection": ingest_open_prompt_injection_dataset,











        "alert": ingest_alert_dataset,











    # Add other datasets here











} 























    if args.dataset in ingestion_functions:











        ingestion_functions[args.dataset](











            normalized_collection=normalized_collection,











            raw_collection=raw_collection,











            edge_collection=edge_collection,











            dataset_path=dataset_path











        )











    else:











        print(f"Error: Unknown dataset '{args.dataset}'.")


if __name__ == "__main__":
    main()