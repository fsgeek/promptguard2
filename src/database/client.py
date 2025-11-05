"""
ArangoDB Client with Connection Pooling
Constitutional Principle VI: Data Provenance
Constitutional Principle VII: Data Architecture

Provides database connectivity for PromptGuard2 and old PromptGuard (migration).
"""

import os
from typing import Optional
import yaml
from arango import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import ArangoError
from pathlib import Path

# Import the new schema
from .schemas.adversarial_prompts import AdversarialPrompt


class DatabaseClient:
    """
    ArangoDB client with connection pooling.

    Usage:
        client = DatabaseClient()
        db = client.get_database()  # PromptGuard2
        old_db = client.get_old_database()  # Old PromptGuard (for migration)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize database client.

        Args:
            config_path: Path to database.yaml config file
        """
        if config_path is None:
            # Default to config/database.yaml in project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "database.yaml"

        self.config = self._load_config(config_path)
        self.client = ArangoClient(hosts=f"http://{self.config['database']['host']}:{self.config['database']['port']}")

        # Password from environment variable (Constitutional Principle VI)
        self.password = os.getenv("ARANGODB_PROMPTGUARD_PASSWORD")
        if not self.password:
            raise ValueError(
                "ARANGODB_PROMPTGUARD_PASSWORD environment variable not set. "
                "Set via: export ARANGODB_PROMPTGUARD_PASSWORD=your_password"
            )

        self._db: Optional[StandardDatabase] = None
        self._old_db: Optional[StandardDatabase] = None

    def _load_config(self, config_path: Path) -> dict:
        """Load database configuration from YAML."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Database config not found at {config_path}. "
                "Run setup tasks T003 first."
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in database config: {e}")

    def get_database(self) -> StandardDatabase:
        """
        Get PromptGuard2 database connection.

        Returns:
            StandardDatabase instance for PromptGuard2

        Raises:
            ArangoError: If connection fails
        """
        if self._db is None:
            try:
                self._db = self.client.db(
                    name=self.config['database']['database_name'],
                    username=self.config['database']['username'],
                    password=self.password,
                    verify=True  # Verify connection on creation
                )
            except ArangoError as e:
                raise ArangoError(
                    f"Failed to connect to PromptGuard2 database at "
                    f"{self.config['database']['host']}:{self.config['database']['port']}: {e}"
                )

        return self._db

    def get_old_database(self) -> StandardDatabase:
        """
        Get old PromptGuard database connection (for migration).

        Returns:
            StandardDatabase instance for old PromptGuard

        Raises:
            ArangoError: If connection fails
        """
        if self._old_db is None:
            try:
                self._old_db = self.client.db(
                    name=self.config['old_database']['database_name'],
                    username=self.config['old_database']['username'],
                    password=self.password,
                    verify=True
                )
            except ArangoError as e:
                raise ArangoError(
                    f"Failed to connect to old PromptGuard database at "
                    f"{self.config['old_database']['host']}:{self.config['old_database']['port']}: {e}"
                )

        return self._old_db

    def get_adversarial_prompts_collection(self):
        """
        Get or create the 'adversarial_prompts' collection.
        """
        db = self.get_database()
        collection_name = "adversarial_prompts"
        if not db.has_collection(collection_name):
            db.create_collection(collection_name)
        return db.collection(collection_name)

    def get_raw_dataset_collection(self, dataset_name: str):
        """
        Get or create a collection for a raw dataset.
        """
        db = self.get_database()
        collection_name = f"{dataset_name}_raw_prompts"
        if not db.has_collection(collection_name):
            db.create_collection(collection_name)
        return db.collection(collection_name)

    def get_edge_collection(self, collection_name: str):
        """
        Get or create an edge collection.
        """
        db = self.get_database()
        if not db.has_collection(collection_name):
            db.create_collection(collection_name, edge=True)
        return db.collection(collection_name)

    def verify_connections(self) -> tuple[bool, bool]:
        """
        Verify both database connections.

        Returns:
            Tuple of (promptguard2_ok, old_promptguard_ok)
        """
        pg2_ok = False
        old_ok = False

        try:
            db = self.get_database()
            db.version()  # Test connection
            pg2_ok = True
        except ArangoError:
            pass

        try:
            old_db = self.get_old_database()
            old_db.version()  # Test connection
            old_ok = True
        except ArangoError:
            pass

        return (pg2_ok, old_ok)

    def close(self):
        """Close database connections."""
        # ArangoDB Python client handles connection pooling automatically
        # No explicit close needed
        self._db = None
        self._old_db = None


# Singleton instance for application-wide use
_client_instance: Optional[DatabaseClient] = None


def get_client() -> DatabaseClient:
    """
    Get singleton database client instance.

    Usage:
        from src.database.client import get_client

        db_client = get_client()
        db = db_client.get_database()
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = DatabaseClient()
    return _client_instance
