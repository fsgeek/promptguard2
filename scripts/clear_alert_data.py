from src.database.client import get_client

def clear_alert_data():
    """
    This script removes all data related to the 'alert' dataset from the database.
    It truncates the 'alert_raw_prompts' collection and removes the corresponding
    entries from the 'adversarial_prompts' and 'normalized_from_raw' collections.
    """
    client = get_client()
    db = client.get_database()

    # 1. Truncate the raw collection
    raw_collection_name = "alert_raw_prompts"
    if db.has_collection(raw_collection_name):
        print(f"Truncating collection: {raw_collection_name}")
        db.collection(raw_collection_name).truncate()

    # 2. Use AQL to remove from normalized and edge collections
    normalized_collection_name = "adversarial_prompts"
    edge_collection_name = "normalized_from_raw"

    # Find the keys of the documents to delete from the normalized collection
    aql_query_find = f"""
    FOR doc IN {normalized_collection_name}
        FILTER doc.source_dataset == 'alert'
        RETURN doc._key
    """
    print(f"Finding documents to delete from {normalized_collection_name}...")
    cursor = db.aql.execute(aql_query_find)
    keys_to_delete = [key for key in cursor]

    if keys_to_delete:
        # The _from attribute is in the format 'collection_name/key'.
        normalized_ids_to_delete = [f"{normalized_collection_name}/{key}" for key in keys_to_delete]
        
        # AQL to delete from edge collection
        aql_query_delete_edge = f"""
        FOR edge IN {edge_collection_name}
            FILTER edge._from IN @from_ids
            REMOVE edge IN {edge_collection_name}
        """
        print(f"Deleting edges from {edge_collection_name}...")
        db.aql.execute(aql_query_delete_edge, bind_vars={'from_ids': normalized_ids_to_delete})
        
        # AQL to delete from normalized collection
        aql_query_delete_norm = f"""
        FOR key IN @keys
            REMOVE key IN {normalized_collection_name}
        """
        print(f"Deleting {len(keys_to_delete)} documents from {normalized_collection_name}...")
        db.aql.execute(aql_query_delete_norm, bind_vars={'keys': keys_to_delete})

    print("Finished clearing 'alert' dataset.")

if __name__ == "__main__":
    clear_alert_data()
