import os
import yaml
import uuid
from typing import List, Dict, Any, Optional, Union
from loguru import logger
from datetime import datetime
import hashlib
import json
import asyncio
from pathlib import Path
import tiktoken
from chromadb_setup import ChromaDBSetup

class IndexBuilder:
    """
    Index Builder: Processes and embeds documents into ChromaDB
    Handles chunking, metadata extraction, and batch operations
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.db_setup = ChromaDBSetup(config_path)
        self.db_setup.initialize_client()
        self.collections = self.db_setup.setup_collections()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        collection_type: str = "main",
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Add documents to the specified collection
        
        Args:
            documents: List of document dicts with 'content', 'metadata', etc.
            collection_type: Which collection to add to ('main', 'code', 'documentation', etc.)
            batch_size: Number of documents to process in each batch
        """
        try:
            collection = self.collections.get(collection_type)
            if not collection:
                raise ValueError(f"Collection type '{collection_type}' not found")
            
            total_docs = len(documents)
            processed_docs = 0
            chunks_created = 0
            
            logger.info(f"Adding {total_docs} documents to {collection_type} collection")
            
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]
                batch_result = self._process_document_batch(batch, collection)
                
                processed_docs += len(batch)
                chunks_created += batch_result['chunks_created']
                
                logger.info(f"Processed {processed_docs}/{total_docs} documents ({chunks_created} chunks)")
            
            return {
                "success": True,
                "documents_processed": processed_docs,
                "chunks_created": chunks_created,
                "collection": collection_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "documents_processed": 0,
                "chunks_created": 0
            }
    
    def _process_document_batch(self, documents: List[Dict], collection) -> Dict[str, Any]:
        """Process a batch of documents into chunks and add to collection"""
        batch_ids = []
        batch_documents = []
        batch_metadatas = []
        chunks_created = 0
        
        for doc in documents:
            chunks = self._chunk_document(doc)
            
            for chunk in chunks:
                chunk_id = self._generate_chunk_id(chunk)
                
                if self._chunk_exists(collection, chunk_id):
                    logger.debug(f"Chunk {chunk_id} already exists, skipping")
                    continue
                
                batch_ids.append(chunk_id)
                batch_documents.append(chunk['content'])
                batch_metadatas.append(chunk['metadata'])
                chunks_created += 1
        
        if batch_ids:
            collection.add(
                ids=batch_ids,
                documents=batch_documents,
                metadatas=batch_metadatas
            )
        
        return {"chunks_created": chunks_created}
    
    def _chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split document into chunks based on content type and size
        """
        content = document.get('content', '')
        metadata = document.get('metadata', {})
        source_type = metadata.get('source_type', 'unknown')
        chunk_size = self.config['vector_store']['chunk_size']
        chunk_overlap = self.config['vector_store']['chunk_overlap']
        
        if source_type == 'code':
            chunks = self._chunk_code(content, chunk_size, chunk_overlap)
        elif source_type == 'markdown' or source_type == 'documentation':
            chunks = self._chunk_markdown(content, chunk_size, chunk_overlap)
        elif source_type == 'slack' or source_type == 'conversation':
            chunks = self._chunk_conversation(content, chunk_size, chunk_overlap)
        else:
            chunks = self._chunk_text(content, chunk_size, chunk_overlap)
        
        enriched_chunks = []
        for i, chunk_content in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk_content),
                'tokens': len(self.tokenizer.encode(chunk_content)),
                'created_at': datetime.now().isoformat()
            })
            
            enriched_chunks.append({
                'content': chunk_content,
                'metadata': chunk_metadata
            })
        
        return enriched_chunks
    
    def _chunk_code(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Chunk code content preserving function/class boundaries"""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_tokens = len(self.tokenizer.encode(line))
            
            if current_size + line_tokens > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                overlap_lines = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else []
                current_chunk = overlap_lines + [line]
                current_size = sum(len(self.tokenizer.encode(l)) for l in current_chunk)
            else:
                current_chunk.append(line)
                current_size += line_tokens
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _chunk_markdown(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Chunk markdown content preserving section boundaries"""
        sections = []
        current_section = []
        
        for line in content.split('\n'):
            if line.startswith('#') and current_section:
                sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        

        chunks = []
        for section in sections:
            section_tokens = len(self.tokenizer.encode(section))
            if section_tokens <= chunk_size:
                chunks.append(section)
            else:
                sub_chunks = self._chunk_text(section, chunk_size, chunk_overlap)
                chunks.extend(sub_chunks)
        
        return chunks
    
    def _chunk_conversation(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Chunk conversation/chat content preserving message boundaries"""
        messages = content.split('\n\n')  
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for message in messages:
            message_tokens = len(self.tokenizer.encode(message))
            
            if current_size + message_tokens > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [message]
                current_size = message_tokens
            else:
                current_chunk.append(message)
                current_size += message_tokens
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _chunk_text(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Generic text chunking with token-based splitting"""
        tokens = self.tokenizer.encode(content)
        chunks = []
        
        for i in range(0, len(tokens), chunk_size - chunk_overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def _generate_chunk_id(self, chunk: Dict[str, Any]) -> str:
        """Generate unique ID for a chunk"""
        content = chunk['content']
        metadata = chunk['metadata']
        hash_input = f"{content}_{metadata.get('file_path', '')}_{metadata.get('chunk_index', 0)}"
        content_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        source_type = metadata.get('source_type', 'doc')
        chunk_id = f"{source_type}_{content_hash}_{uuid.uuid4().hex[:8]}"
        
        return chunk_id
    
    def _chunk_exists(self, collection, chunk_id: str) -> bool:
        """Check if chunk already exists in collection"""
        try:
            result = collection.get(ids=[chunk_id])
            return len(result['ids']) > 0
        except:
            return False
    
    def reindex_collection(self, collection_type: str = "main") -> Dict[str, Any]:
        """Completely rebuild a collection index"""
        try:
            logger.info(f"Starting reindex of {collection_type} collection")
            
            collection_name = f"{self.config['vector_store']['collection_name']}"
            if collection_type != "main":
                collection_name += f"_{collection_type}"
            
            success = self.db_setup.reset_collection(collection_name)
            if not success:
                raise Exception(f"Failed to reset collection {collection_name}")
            
          
            self.collections = self.db_setup.setup_collections()
            
            logger.info(f"Collection {collection_type} reindexed successfully")
            return {
                "success": True,
                "collection": collection_type,
                "message": "Collection reset and ready for new documents",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reindexing collection: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_indexing_stats(self) -> Dict[str, Any]:
        """Get comprehensive indexing statistics"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "collections": {},
            "total_documents": 0,
            "total_chunks": 0,
            "config": {
                "chunk_size": self.config['vector_store']['chunk_size'],
                "chunk_overlap": self.config['vector_store']['chunk_overlap'],
                "embedding_model": self.config['vector_store']['embedding_model']
            }
        }
        
        try:
            for collection_name, collection in self.collections.items():
                count = collection.count()
                metadata = collection.metadata or {}
                
                stats["collections"][collection_name] = {
                    "document_count": count,
                    "metadata": metadata
                }
                stats["total_chunks"] += count
            
            avg_chunks_per_doc = 3 
            stats["estimated_documents"] = stats["total_chunks"] // avg_chunks_per_doc
            
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    async def build_index_from_sources(self, data_sources: List[str] = None) -> Dict[str, Any]:
        """Build index from configured data sources"""
        if not data_sources:
            data_sources = ['codebase', 'documentation', 'slack', 'pr', 'ticket']
        
        results = {
            "success": True,
            "sources_processed": [],
            "total_documents": 0,
            "total_chunks": 0,
            "errors": []
        }
        
        try:
            
            for source in data_sources:
                try:
                    if source == 'codebase':
                        from data_sources.code_parser import CodeParser
                        parser = CodeParser()
                        documents = await parser.parse_codebase()
                        
                    elif source == 'documentation':
                        from data_sources.doc_ingestor import DocIngestor
                        ingestor = DocIngestor()
                        documents = await ingestor.ingest_docs()
                               
                    elif source == "slack":
                        from data_sources.slack_parser import SlackParser
                        parser = SlackParser()
                        documents = await parser.parse_export()

                    elif source == "pr":
                        from data_sources.pr_fetcher import PRFetcher
                        parser = PRFetcher()
                        documents = await parser.fetch_prs()

                    elif source == "ticket":
                        from data_sources.ticket_fetcher import TicketFetcher
                        parser = TicketFetcher()
                        documents = await parser.fetch_tickets()

                    else:
                        logger.warning(f"Unknown data source: {source}")
                        continue
                    
                    result = self.add_documents(documents, source)
                    
                    if result['success']:
                        results["sources_processed"].append(source)
                        results["total_documents"] += result['documents_processed']
                        results["total_chunks"] += result['chunks_created']
                    else:
                        results["errors"].append(f"{source}: {result['error']}")
                        
                except Exception as e:
                    logger.error(f"Error processing {source}: {str(e)}")
                    results["errors"].append(f"{source}: {str(e)}")
            
            if results["errors"]:
                results["success"] = False
            
        except Exception as e:
            results["success"] = False
            results["errors"].append(f"General error: {str(e)}")
        
        return results

def quick_index(documents: List[Dict], collection_type: str = "main") -> Dict[str, Any]:
    """Quick indexing function for simple use cases"""
    builder = IndexBuilder()
    return builder.add_documents(documents, collection_type)

def rebuild_index(collection_type: str = "main") -> Dict[str, Any]:
    """Quickly rebuild an index"""
    builder = IndexBuilder()
    return builder.reindex_collection(collection_type)

if __name__ == "__main__":

    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        builder = IndexBuilder()
        
        if command == "stats":
            stats = builder.get_indexing_stats()
            print("Indexing Statistics:")
            print(json.dumps(stats, indent=2))
            
        elif command == "reindex":
            collection_type = sys.argv[2] if len(sys.argv) > 2 else "main"
            result = builder.reindex_collection(collection_type)
            print(f"Reindex result: {result}")
            
        elif command == "build":
            sources = sys.argv[2:] if len(sys.argv) > 2 else None
            result = asyncio.run(builder.build_index_from_sources(sources))
            print(f"Build result: {result}")
            
        else:
            print("Available commands: stats, reindex [collection], build [sources...]")
    else:
        print("Usage: python index_builder.py [stats|reindex|build]")