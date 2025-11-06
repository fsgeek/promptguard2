import argparse
from arango.collection import StandardCollection
from src.database.client import get_client

def create_db_indexes():
    client = get_client()
    db = client.get_database()
    normalized_collection = client.get_adversarial_prompts_collection()

    print("Creating indexes for adversarial_prompts collection...")

    # Hash Indexes
    hash_fields = ["source_dataset", "source_file", "split", "attack_type", "domain", "is_adversarial"]
    existing_indexes = normalized_collection.indexes()
    existing_index_names = [idx['name'] for idx in existing_indexes]

    for field in hash_fields:
        index_name = f"idx_{field}"
        if index_name not in existing_index_names:
            normalized_collection.add_hash_index(fields=[field], unique=False, name=index_name)
            print(f"Created hash index for {field}")
        else:
            print(f"Hash index for {field} already exists.")

    # ArangoSearch View
    view_name = "adversarial_prompts_search_view"
    existing_views = db.views()
    existing_view_names = [view['name'] for view in existing_views]

    if view_name not in existing_view_names:
        db.create_view(
            name=view_name,
            view_type="arangosearch",
            properties={
                "links": {
                    normalized_collection.name: {
                        "fields": {
                            "prompt": {"analyzers": ["text_en", "identity"]},
                            "user_task": {"analyzers": ["text_en", "identity"]},
                            "expected_output": {"analyzers": ["text_en", "identity"]},
                            "attack_objectives": {"analyzers": ["text_en", "identity"]},
                            "prompt_components": {"analyzers": ["text_en", "identity"]},
                            "tags": {"analyzers": ["text_en", "identity"]}
                        }
                    }
                }
            }
        )
        print(f"Created ArangoSearch view: {view_name}")
    else:
        print(f"ArangoSearch view {view_name} already exists.")

    print("Finished creating indexes and views.")

if __name__ == "__main__":
    create_db_indexes()
