from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional

class EduHubDB:
    def __init__(self, connection_string: str = 'mongodb://localhost:27017/'):
        print("Initializing database connection...")
        self.client = MongoClient(connection_string)
        self.db = self.client['eduhub_db']
        self.initialize_collections()

    def initialize_collections(self):
        """Initialize collections with validation rules"""

        def setup_collection(name: str, schema: dict):
            if name not in self.db.list_collection_names():
                print(f"Creating collection: {name}")
                self.db.create_collection(name)
            print(f"Applying validation to collection: {name}")
            self.db.command("collMod", name, validator=schema)