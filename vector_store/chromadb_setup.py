import os
import yaml
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from typing import Dict, List, Optional, Any
from loguru import logger
import shutil
from datetime import datetime
import chromadb
from chromadb import PersistentClient
import logging
import chromadb
chromadb.telemetry.capture = lambda *args, **kwargs: None
from dotenv import load_dotenv
load_dotenv()


os.environ["ANONYMIZED_TELEMETRY"] = "False" 
os.environ["CHROMA_TELEMETRY"] = "False"

# Reduce ChromaDB logging verbosity
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)

class ChromaDBSetup:
    """
    ChromaDB Setup and Management
    Handles database initialization, collection management, and configuration
    """
    
    def __init__(self, config_path: str = None, user_id: str = None, org_id: str = None):
        self.config = self._load_config(config_path)
        self.user_id = user_id or "demo_user"
        self.org_id = org_id or "demo_org"
        self.demo_mode = self.user_id == "demo_user"
        self.db_path = self._get_db_path()
        self.client = None
        self.collections = {}
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_db_path(self) -> str:
        """Get the database storage path with org isolation"""
        if self.demo_mode:
            db_path = os.path.join(
                os.path.dirname(__file__), "chroma_db_demo"
            )
        else:
            db_path = os.path.join(
                os.path.dirname(__file__), "chroma_db", self.org_id
            )
        os.makedirs(db_path, exist_ok=True)
        return db_path
    
    def _get_collection_name(self, base_name: str) -> str:
        """Get collection name with tenant isolation"""
        if self.demo_mode:
            return f"demo_{base_name}"
        return f"{self.org_id}_{base_name}"

    
    
    def initialize_client(self) -> chromadb.PersistentClient:
        """Initialize ChromaDB client with persistent storage"""
        try:
            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.db_path,
                anonymized_telemetry=False
            )
            
            self.client = PersistentClient(path=self.db_path)
            
            logger.info(f"ChromaDB client initialized at: {self.db_path}")
            return self.client
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise
    
    def setup_collections(self) -> Dict[str, Any]:
        """Set up all required collections with appropriate embedding functions"""
        if not self.client:
            self.initialize_client()
        
        collections_info = {}
        
        main_collection_name = self._get_collection_name(self.config['vector_store']['collection_name'])
        main_collection = self._create_or_get_collection(
            name=main_collection_name,
            description="Main knowledge base for code, docs, PRs, and team context"
        )
        collections_info['main'] = main_collection
        
        specialized_collections = {
            'code': 'Code snippets and functions',
            'documentation': 'Documentation and README files', 
            'pull_requests': 'GitHub PR descriptions and discussions',
            'slack_messages': 'Team Slack conversations and context',
            'tickets': 'Jira tickets and issue tracking'
        }
        
        for collection_name, description in specialized_collections.items():
            full_name = self._get_collection_name(f"{self.config['vector_store']['collection_name']}_{collection_name}")
            collection = self._create_or_get_collection(
                name=full_name,
                description=description
            )
            collections_info[collection_name] = collection
        
        self.collections = collections_info
        logger.info(f"Set up {len(collections_info)} collections for {'demo mode' if self.demo_mode else f'org {self.org_id}'}")
        
        return collections_info
    
    def _create_or_get_collection(self, name: str, description: str = None) -> chromadb.Collection:
        """Create a new collection or get existing one"""
        try:
            
            embedding_function = self._get_embedding_function()
    
            try:
                collection = self.client.get_collection(
                    name=name,
                    embedding_function=embedding_function
                )
                logger.info(f"Retrieved existing collection: {name}")
                
            except Exception:
                metadata = {"description": description} if description else {}
                if not self.demo_mode:
                    metadata.update({
                        "org_id": self.org_id,
                        "created_by": self.user_id,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                else:
                    metadata.update({
                        "demo_mode": True,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                collection = self.client.create_collection(
                    name=name,
                    embedding_function=embedding_function,
                    metadata=metadata
                )
                logger.info(f"Created new collection: {name}")
            
            return collection
            
        except Exception as e:
            logger.error(f"Error with collection {name}: {str(e)}")
            raise
    
    def _get_embedding_function(self):
        """Get the configured embedding function"""
        embedding_model = self.config['vector_store']['embedding_model']
        
        if embedding_model.startswith('text-embedding'):
            return embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=embedding_model
            )
        elif embedding_model.startswith('sentence-transformers'):
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model.replace('sentence-transformers/', '')
            )
        else:
            logger.warning(f"Unknown embedding model {embedding_model}, defaulting to OpenAI")
            return embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name="text-embedding-ada-002"
            )
    
    def get_user_collections(self) -> List[str]:
        """Get all collections for current user/org"""
        if not self.client:
            self.initialize_client()
        
        try:
            all_collections = self.client.list_collections()
            if self.demo_mode:
                return [c.name for c in all_collections if c.name.startswith("demo_")]
            else:
                return [c.name for c in all_collections if c.name.startswith(f"{self.org_id}_")]
        except Exception as e:
            logger.error(f"Error getting user collections: {str(e)}")
            return []
    
    def get_collection_stats(self, collection_name: str = None) -> Dict[str, Any]:
        """Get statistics for a specific collection or all collections"""
        if not self.client:
            self.initialize_client()
        
        stats = {}
        
        if collection_name:
            try:
                full_name = self._get_collection_name(collection_name) if not collection_name.startswith(('demo_', self.org_id)) else collection_name
                collection = self.client.get_collection(full_name)
                stats[collection_name] = {
                    "count": collection.count(),
                    "metadata": collection.metadata or {}
                }
            except Exception as e:
                stats[collection_name] = {"error": str(e)}
        else:
            try:
                user_collections = self.get_user_collections()
                for collection_name in user_collections:
                    collection = self.client.get_collection(collection_name)
                    stats[collection_name] = {
                        "count": collection.count(),
                        "metadata": collection.metadata or {}
                    }
            except Exception as e:
                logger.error(f"Error getting collection stats: {str(e)}")
                stats = {"error": str(e)}
        
        return stats
    
    def reset_collection(self, collection_name: str) -> bool:
        """Reset (delete and recreate) a specific collection"""
        if not self.client:
            self.initialize_client()
        
        try:
            full_name = self._get_collection_name(collection_name)
            
            try:
                self.client.delete_collection(full_name)
                logger.info(f"Deleted collection: {full_name}")
            except Exception:
                logger.info(f"Collection {full_name} didn't exist, creating new")
            
            embedding_function = self._get_embedding_function()
            collection = self.client.create_collection(
                name=full_name,
                embedding_function=embedding_function
            )
            
            logger.info(f"Reset collection: {full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting collection {collection_name}: {str(e)}")
            return False
    
    def delete_user_collections(self) -> bool:
        """Delete all collections for current user/org"""
        if not self.client:
            self.initialize_client()

        try:
            user_collections = self.get_user_collections()
            for collection_name in user_collections:
                self.client.delete_collection(collection_name)
                logger.info(f"Deleted collection: {collection_name}")
            logger.info(f"All collections deleted for {'demo mode' if self.demo_mode else f'org {self.org_id}'}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user collections: {str(e)}")
            return False

    def delete_all_collections(self) -> bool:
        """Delete all collections in the ChromaDB client"""
        if not self.client:
            self.initialize_client()

        try:
            for collection in self.client.list_collections():
                self.client.delete_collection(collection.name)
                logger.info(f"Deleted collection: {collection.name}")
            logger.info("All collections deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting all collections: {str(e)}")
            return False
    
    def backup_database(self, backup_path: str = None) -> str:
        """Create a backup of the entire ChromaDB database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(
                os.path.dirname(self.db_path), 
                f"chroma_backup_{timestamp}"
            )
        
        try:
            shutil.copytree(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            raise
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path)
            
            shutil.copytree(backup_path, self.db_path)
            
            self.client = None
            self.initialize_client()
            
            logger.info(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring database: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on ChromaDB setup"""
        health_info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "database_path": self.db_path,
            "database_exists": os.path.exists(self.db_path),
            "client_initialized": self.client is not None,
            "user_id": self.user_id,
            "org_id": self.org_id,
            "demo_mode": self.demo_mode,
            "collections": {},
            "total_documents": 0,
            "status": "unknown"
        }
        
        try:
            if not self.client:
                self.initialize_client()
            
            user_collections = self.get_user_collections()
            total_docs = 0
            
            for collection_name in user_collections:
                collection = self.client.get_collection(collection_name)
                count = collection.count()
                health_info["collections"][collection_name] = {
                    "document_count": count,
                    "metadata": collection.metadata or {}
                }
                total_docs += count
            
            health_info["total_documents"] = total_docs
            health_info["status"] = "healthy" if total_docs > 0 else "empty"
            
        except Exception as e:
            health_info["status"] = "error"
            health_info["error"] = str(e)
            logger.error(f"Health check failed: {str(e)}")
        
        return health_info
    
    def migrate_schema(self, version: str = "v1") -> bool:
        """Handle schema migrations for future versions"""
        try:
            logger.info(f"Schema migration to {version} completed (no changes needed)")
            return True
            
        except Exception as e:
            logger.error(f"Schema migration failed: {str(e)}")
            return False

def setup_chromadb(config_path: str = None, user_id: str = None, org_id: str = None) -> ChromaDBSetup:
    """Quick setup function to initialize ChromaDB"""
    setup = ChromaDBSetup(config_path, user_id, org_id)
    setup.initialize_client()
    setup.setup_collections()
    return setup

def get_chromadb_client(config_path: str = None, user_id: str = None, org_id: str = None) -> chromadb.PersistentClient:
    """Get a configured ChromaDB client"""
    setup = ChromaDBSetup(config_path, user_id, org_id)
    return setup.initialize_client()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        user_id = sys.argv[2] if len(sys.argv) > 2 else None
        org_id = sys.argv[3] if len(sys.argv) > 3 else None
        
        setup = ChromaDBSetup(user_id=user_id, org_id=org_id)
        
        if command == "init":
            setup.initialize_client()
            setup.setup_collections()
            print("ChromaDB initialized successfully")
            
        elif command == "stats":
            setup.initialize_client()
            stats = setup.get_collection_stats()
            print("Collection Statistics:")
            for name, info in stats.items():
                print(f"  {name}: {info}")
                
        elif command == "health":
            health = setup.health_check()
            print("Health Check Results:")
            for key, value in health.items():
                print(f"  {key}: {value}")
                
        elif command == "backup":
            setup.initialize_client()
            backup_path = setup.backup_database()
            print(f"Backup created at: {backup_path}")
            
        else:
            print("Available commands: init, stats, health, backup")
    else:
        print("Usage: python chromadb_setup.py [init|stats|health|backup] [user_id] [org_id]")