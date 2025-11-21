"""Sequence loader for multi-turn attack datasets.

Loads evaluation sequences from various sources:
- XGuard-Train: SafeMTData synthetic gradual attacks (Parquet)
- MHJ: Scale AI human red-team jailbreaks (CSV)
- Benign: TensorTrust/ShareGPT benign conversations (ArangoDB)
"""

from typing import List, Optional
from pathlib import Path
import pandas as pd
import json

from src.database.schemas.phase3_evaluation import (
    EvaluationSequence,
    AttackLabel,
    SourceDataset,
)


class SequenceLoader:
    """Load multi-turn evaluation sequences from datasets.

    Usage:
        loader = SequenceLoader(db=arango_db)
        sequences = loader.load(dataset="xguard_train", sample=10)
    """

    def __init__(self, db=None):
        """Initialize loader.

        Args:
            db: ArangoDB database connection (optional, required for benign dataset)
        """
        self.db = db

    def load(
        self,
        dataset: str,
        sample: Optional[int] = None,
    ) -> List[EvaluationSequence]:
        """Load evaluation sequences from specified dataset.

        Args:
            dataset: Dataset name ("xguard_train", "mhj", "benign")
            sample: If provided, load only first N sequences

        Returns:
            List of EvaluationSequence objects

        Raises:
            ValueError: If dataset name not recognized
            FileNotFoundError: If dataset file not found
        """
        if dataset == "xguard_train":
            return self._load_xguard_train(sample=sample)
        elif dataset == "mhj":
            return self._load_mhj(sample=sample)
        elif dataset == "benign":
            return self._load_benign(sample=sample)
        else:
            raise ValueError(
                f"Unknown dataset: {dataset}. "
                "Supported: xguard_train, mhj, benign"
            )

    def _load_xguard_train(self, sample: Optional[int] = None) -> List[EvaluationSequence]:
        """Load XGuard-Train synthetic gradual attack sequences.

        Dataset: data/raw_datasets/safemtdata/attack_600.parquet
        Schema: id, query_id, category, actor_name, relationship, plain_query, multi_turn_queries
        """
        parquet_path = Path("data/raw_datasets/safemtdata/attack_600.parquet")

        if not parquet_path.exists():
            raise FileNotFoundError(
                f"XGuard-Train dataset not found at {parquet_path}. "
                "Download from SafeMTData repository."
            )

        # Load parquet
        df = pd.read_parquet(parquet_path)

        # Apply sampling
        if sample is not None:
            df = df.head(sample)

        # Convert to EvaluationSequence objects
        sequences = []
        for idx, row in df.iterrows():
            attack_id = f"xguard_{row['id']}"

            # multi_turn_queries is a numpy array of strings
            turns = list(row["multi_turn_queries"])

            sequence = EvaluationSequence(
                attack_id=attack_id,
                label=AttackLabel.JAILBREAK,  # XGuard is all jailbreaks
                source_dataset=SourceDataset.XGUARD_TRAIN,
                turns=turns,
                metadata={
                    "category": row["category"],
                    "plain_query": row["plain_query"],
                    "query_id": int(row["query_id"]),
                },
            )
            sequences.append(sequence)

        return sequences

    def _load_mhj(self, sample: Optional[int] = None) -> List[EvaluationSequence]:
        """Load MHJ (Multi-turn Human Jailbreaks) sequences.

        Dataset: data/raw_datasets/MHJ/harmbench_behaviors.csv
        Schema: Source, temperature, tactic, question_id, time_spent, submission_message,
                message_0 through message_100 (JSON strings with role/body)
                
        Phase 4 update: Now preserves assistant responses for harm manifestation analysis.
        """
        csv_path = Path("data/raw_datasets/MHJ/harmbench_behaviors.csv")

        if not csv_path.exists():
            raise FileNotFoundError(
                f"MHJ dataset not found at {csv_path}. "
                "Download from HarmBench repository."
            )

        # Load CSV
        df = pd.read_csv(csv_path)

        # Apply sampling
        if sample is not None:
            df = df.head(sample)

        # Convert to EvaluationSequence objects
        sequences = []
        for idx, row in df.iterrows():
            attack_id = f"mhj_{row['question_id']}"

            # Extract user turns AND assistant responses from message_0 through message_100
            user_turns = []
            assistant_responses = []
            
            for i in range(101):  # message_0 to message_100
                col_name = f"message_{i}"
                if col_name not in row or pd.isna(row[col_name]):
                    # No more messages in this sequence
                    break

                # Parse JSON message
                try:
                    message = json.loads(row[col_name])
                    role = message.get("role", "")
                    body = message.get("body", "")

                    # Separate user and assistant turns
                    if role == "user":
                        user_turns.append(body)
                    elif role == "assistant":
                        assistant_responses.append(body)
                except (json.JSONDecodeError, TypeError):
                    # Skip malformed messages
                    continue

            # Only create sequence if we have at least one user turn
            if user_turns:
                sequence = EvaluationSequence(
                    attack_id=attack_id,
                    label=AttackLabel.JAILBREAK,  # MHJ is all jailbreaks
                    source_dataset=SourceDataset.MHJ,
                    turns=user_turns,
                    assistant_responses=assistant_responses if assistant_responses else None,
                    metadata={
                        "tactic": row["tactic"],
                        "source": row["Source"],
                    },
                )
                sequences.append(sequence)

        return sequences

    def _load_benign(self, sample: Optional[int] = None) -> List[EvaluationSequence]:
        """Load benign sequences from ArangoDB.

        Sequences were extracted in Phase 2 (T006) from TensorTrust and ShareGPT.
        """
        if self.db is None:
            raise ValueError(
                "Database connection required to load benign sequences. "
                "Pass db parameter to SequenceLoader constructor."
            )

        # Query phase3_evaluation_sequences collection for benign sequences
        coll = self.db.collection("phase3_evaluation_sequences")

        aql = """
        FOR doc IN phase3_evaluation_sequences
            FILTER doc.label == "benign"
            SORT doc.created_at ASC
            RETURN doc
        """

        cursor = self.db.aql.execute(aql)
        docs = list(cursor)

        # Apply sampling
        if sample is not None:
            docs = docs[:sample]

        # Convert to EvaluationSequence objects
        sequences = []
        for doc in docs:
            sequence = EvaluationSequence(
                attack_id=doc["_key"],
                label=AttackLabel(doc["label"]),
                source_dataset=SourceDataset(doc["source_dataset"]),
                turns=doc["turns"],
                metadata=doc.get("metadata", {}),
            )
            sequences.append(sequence)

        return sequences

    def load_and_insert(
        self,
        dataset: str,
        sample: Optional[int] = None,
    ) -> int:
        """Load sequences and insert to database (idempotent).

        Args:
            dataset: Dataset name
            sample: Optional sampling limit

        Returns:
            Number of sequences inserted

        Raises:
            ValueError: If database connection not available
        """
        if self.db is None:
            raise ValueError(
                "Database connection required for load_and_insert. "
                "Pass db parameter to SequenceLoader constructor."
            )

        sequences = self.load(dataset=dataset, sample=sample)

        # Insert to phase3_evaluation_sequences collection
        coll = self.db.collection("phase3_evaluation_sequences")

        inserted_count = 0
        for sequence in sequences:
            doc = sequence.model_dump(mode="json")
            doc["_key"] = sequence.attack_id

            # Idempotent insert (overwrite if exists)
            coll.insert(doc, overwrite=True)
            inserted_count += 1

        return inserted_count
