import argparse
from arango.collection import StandardCollection
from src.database.client import get_client

def clear_dataset_data(dataset_name: str):
    client = get_client()
    db = client.get_database()

    normalized_collection = client.get_adversarial_prompts_collection()
    raw_collection_name = f"{dataset_name}_raw_prompts"
    raw_collection = db.collection(raw_collection_name)
    edge_collection = client.get_edge_collection("normalized_from_raw")

    print(f"Clearing data for dataset: {dataset_name}")

    print(f"Clearing data for dataset: {dataset_name}")

    # 1. Delete normalized prompts for this dataset
    aql_query_normalized = f"""
        FOR doc IN {normalized_collection.name}
        FILTER doc.source_dataset == @dataset_name
        REMOVE doc IN {normalized_collection.name} OPTIONS {{ waitForSync: true }}
    """
    cursor = db.aql.execute(aql_query_normalized, bind_vars={'dataset_name': dataset_name})
    normalized_stats = cursor.statistics()
    deleted_normalized_docs = normalized_stats.get('writes_removed', 0) if normalized_stats else 0
    print(f"Deleted {deleted_normalized_docs} documents from {normalized_collection.name}.")

    # 2. Truncate the raw collection for this dataset
    if db.has_collection(raw_collection.name):
        raw_collection.truncate()
        print(f"Truncated raw collection: {raw_collection.name}")
    else:
        print(f"Raw collection {raw_collection.name} does not exist, skipping truncation.")

    print(f"Finished clearing data for dataset: {dataset_name}")

    print(f"Finished clearing data for dataset: {dataset_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clear data for a specific dataset from ArangoDB.")
    parser.add_argument("dataset", type=str, help="The name of the dataset to clear (e.g., 'harmbench', 'open_prompt_injection').")
    args = parser.parse_args()
    clear_dataset_data(args.dataset)
