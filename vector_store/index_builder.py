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
from vector_store.chromadb_setup import ChromaDBSetup


class IndexBuilder:
    """
    Enhanced Index Builder: Processes and embeds documents into ChromaDB
    Now with enriched metadata integration, quality filtering, and semantic enhancement
    """
    
    def __init__(self, config_path: str = None, user_id: str = None, org_id: str = None):
        self.config = self._load_config(config_path)
        self.user_id = user_id or "demo_user"
        self.org_id = org_id or "demo_org"
        self.demo_mode = self.user_id == "demo_user"
        self.db_setup = ChromaDBSetup(config_path, user_id, org_id)
        self.db_setup.initialize_client()
        self.collections = self.db_setup.setup_collections()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        
        self.quality_threshold = 0.5
        self.enrichment_config = {
            'use_integration_filtering': True,
            'use_semantic_enhancement': True,
            'skip_high_severity_issues': True,
            'prioritize_enriched_content': True,
            'include_relationship_metadata': True
        }
        
       
        self.index_metadata = {
            'documents_skipped': [],
            'quality_distribution': {},
            'content_summary': {},
            'issues_summary': {},
            'relationship_summary': {},
            'semantic_summary': {}
        }
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        collection_type: str = "main",
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Enhanced document addition with integration-aware filtering and semantic enhancement
        
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
            
          
            self._reset_index_metadata()
            
            logger.info(f"Adding {total_docs} documents to {collection_type} collection with enhanced processing ({'demo mode' if self.demo_mode else f'org {self.org_id}'})")
            
          
            filtered_documents = self._filter_documents_by_quality(documents)
            
            logger.info(f"Filtered to {len(filtered_documents)} documents based on quality and integration analysis")
            
            for i in range(0, len(filtered_documents), batch_size):
                batch = filtered_documents[i:i + batch_size]
                batch_result = self._process_document_batch(batch, collection)
                
                processed_docs += len(batch)
                chunks_created += batch_result['chunks_created']
                
                logger.info(f"Processed {processed_docs}/{len(filtered_documents)} documents ({chunks_created} chunks)")
            
            
            index_summary = self._generate_index_summary(documents, filtered_documents)
            
            return {
                "success": True,
                "documents_processed": processed_docs,
                "chunks_created": chunks_created,
                "collection": collection_type,
                "user_id": self.user_id,
                "org_id": self.org_id,
                "demo_mode": self.demo_mode,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                
                "enriched_indexing": {
                    "total_input_documents": total_docs,
                    "filtered_documents": len(filtered_documents),
                    "documents_skipped": len(self.index_metadata['documents_skipped']),
                    "quality_filtering_enabled": self.enrichment_config['use_integration_filtering'],
                    "semantic_enhancement_enabled": self.enrichment_config['use_semantic_enhancement'],
                    "index_summary": index_summary
                }
            }
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "documents_processed": 0,
                "chunks_created": 0
            }
    
    def _reset_index_metadata(self):
        """Reset index metadata for new operation"""
        self.index_metadata = {
            'documents_skipped': [],
            'quality_distribution': {},
            'content_summary': {},
            'issues_summary': {},
            'relationship_summary': {},
            'semantic_summary': {}
        }
    
    def _filter_documents_by_quality(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter documents based on integration quality and issues"""
        if not self.enrichment_config['use_integration_filtering']:
            return documents
        
        filtered_documents = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            integration = metadata.get('integration', {})
            

            quality_score = integration.get('quality_score', 1.0) 
            
          
            issues = integration.get('issues', [])
            has_high_severity_issues = any(issue.get('severity') == 'high' for issue in issues)
            
            skip_reason = None
            
            if quality_score < self.quality_threshold:
                skip_reason = f"Low quality score: {quality_score:.2f} < {self.quality_threshold}"
            elif has_high_severity_issues and self.enrichment_config['skip_high_severity_issues']:
                high_severity_issues = [issue for issue in issues if issue.get('severity') == 'high']
                skip_reason = f"High severity issues: {[issue.get('type', 'unknown') for issue in high_severity_issues]}"
            
            if skip_reason:
                self.index_metadata['documents_skipped'].append({
                    'document_id': self._generate_document_id(doc),
                    'source_type': metadata.get('source_type', 'unknown'),
                    'name': metadata.get('name', 'unknown'),
                    'reason': skip_reason,
                    'quality_score': quality_score,
                    'issues': [issue.get('type', 'unknown') for issue in issues]
                })
                logger.debug(f"Skipping document: {skip_reason}")
                continue
            
            filtered_documents.append(doc)
        
        return filtered_documents
    
    def _generate_document_id(self, doc: Dict[str, Any]) -> str:
        """Generate a readable document ID for tracking"""
        metadata = doc.get('metadata', {})
        source_type = metadata.get('source_type', 'unknown')
        name = metadata.get('name', '')
        file_path = metadata.get('file_path', '')
        
        if name:
            return f"{source_type}:{name}"
        elif file_path:
            return f"{source_type}:{file_path}"
        else:
            content_hash = hashlib.md5(doc.get('content', '').encode()).hexdigest()[:8]
            return f"{source_type}:{content_hash}"
    
    def _process_document_batch(self, documents: List[Dict], collection) -> Dict[str, Any]:
        """Enhanced batch processing with semantic enhancement"""
        batch_ids = []
        batch_documents = []
        batch_metadatas = []
        chunks_created = 0
        
        for doc in documents:
      
            chunks = self._chunk_document_enhanced(doc)
            
            for chunk in chunks:
                chunk_id = self._generate_chunk_id(chunk)
                
                if self._chunk_exists(collection, chunk_id):
                    logger.debug(f"Chunk {chunk_id} already exists, skipping")
                    continue
                
     
                enhanced_metadata = self._enhance_chunk_metadata(chunk, doc)
                enhanced_metadata['user_id'] = self.user_id
                enhanced_metadata['org_id'] = self.org_id
                enhanced_metadata['demo_mode'] = self.demo_mode
                
                batch_ids.append(chunk_id)
                batch_documents.append(chunk['content'])
                batch_metadatas.append(enhanced_metadata)
                chunks_created += 1
                
            
                self._update_index_metadata(doc, chunk)
        
        if batch_ids:
            collection.add(
                ids=batch_ids,
                documents=batch_documents,
                metadatas=batch_metadatas
            )
        
        return {"chunks_created": chunks_created}
    
    def _chunk_document_enhanced(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced document chunking with semantic awareness"""
        content = document.get('content', '')
        metadata = document.get('metadata', {})
        source_type = metadata.get('source_type', 'unknown')
        chunk_size = self.config['vector_store']['chunk_size']
        chunk_overlap = self.config['vector_store']['chunk_overlap']
        

        enrichment = metadata.get('enrichment', {})
        

        if source_type == 'code':
            chunks = self._chunk_code_enhanced(content, chunk_size, chunk_overlap, enrichment)
        elif source_type in ['markdown', 'documentation']:
            chunks = self._chunk_markdown_enhanced(content, chunk_size, chunk_overlap, enrichment)
        elif source_type in ['slack', 'conversation']:
            chunks = self._chunk_conversation(content, chunk_size, chunk_overlap)
        else:
            chunks = self._chunk_text(content, chunk_size, chunk_overlap)
        

        enriched_chunks = []
        for i, chunk_content in enumerate(chunks):
            chunk_metadata = metadata.copy()
            
          
            cleaned_metadata = self._clean_metadata_for_storage(chunk_metadata)
            
            cleaned_metadata.update({
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk_content),
                'tokens': len(self.tokenizer.encode(chunk_content)),
                'indexed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'indexed_by': self.user_id
            })
            
            enriched_chunks.append({
                'content': chunk_content,
                'metadata': cleaned_metadata
            })
        
        return enriched_chunks
    
    def _chunk_code_enhanced(self, content: str, chunk_size: int, chunk_overlap: int, enrichment: Dict[str, Any]) -> List[str]:
        """Enhanced code chunking using enrichment data"""

        complexity = enrichment.get('complexity', 'moderate')
        
        if complexity == 'simple':

            effective_chunk_size = min(chunk_size, chunk_size // 2)
        elif complexity == 'complex':
 
            effective_chunk_size = min(chunk_size * 2, chunk_size + 200)
        else:
            effective_chunk_size = chunk_size
        
        return self._chunk_code(content, effective_chunk_size, chunk_overlap)
    
    def _chunk_markdown_enhanced(self, content: str, chunk_size: int, chunk_overlap: int, enrichment: Dict[str, Any]) -> List[str]:
        """Enhanced markdown chunking using enrichment data"""
   
        structure = enrichment.get('structure', {})
        
        if structure.get('has_headers', False):
 
            return self._chunk_markdown(content, chunk_size, chunk_overlap)
        else:
 
            return self._chunk_text(content, chunk_size, chunk_overlap)
    
    def _enhance_chunk_metadata(self, chunk: Dict[str, Any], original_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance chunk metadata with semantic information"""
        metadata = chunk['metadata'].copy()
        original_metadata = original_doc.get('metadata', {})
        

        enrichment = original_metadata.get('enrichment', {})
        integration = original_metadata.get('integration', {})
        
        if enrichment and self.enrichment_config['use_semantic_enhancement']:
 
            metadata['enriched_purpose'] = enrichment.get('purpose', 'unknown')
            metadata['enriched_category'] = enrichment.get('category', 'unknown')
            metadata['enriched_complexity'] = enrichment.get('complexity', 'unknown')

            if 'llm_summary' in enrichment:
                metadata['llm_summary'] = enrichment['llm_summary']
        
        if integration and self.enrichment_config['include_relationship_metadata']:
    
            metadata['integration_quality'] = integration.get('quality_score', 1.0)
            
 
            relationships = integration.get('relationships', [])
            metadata['relationship_count'] = len(relationships)
            
      
            if relationships:
                rel_types = list(set(rel.get('type', 'unknown') for rel in relationships))
                metadata['relationship_types'] = ','.join(rel_types)
        
        return metadata
    
    def _clean_metadata_for_storage(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata to only include types supported by ChromaDB"""
        cleaned = {}
        
        for key, value in metadata.items():
        
            if isinstance(value, (str, int, float, bool, type(None))):
                cleaned[key] = value
            elif isinstance(value, dict):
        
                try:
                    cleaned[f"{key}_json"] = json.dumps(value)
                except:
                    pass
            elif isinstance(value, list):
            
                if all(isinstance(item, str) for item in value):
                    cleaned[key] = ','.join(value)
                else:
                    try:
                        cleaned[f"{key}_json"] = json.dumps(value)
                    except:
                        pass
        
        return cleaned
    
    def _update_index_metadata(self, doc: Dict[str, Any], chunk: Dict[str, Any]):
        """Update index-level metadata tracking"""
        metadata = doc.get('metadata', {})
        source_type = metadata.get('source_type', 'unknown')
        
   
        if source_type not in self.index_metadata['content_summary']:
            self.index_metadata['content_summary'][source_type] = 0
        self.index_metadata['content_summary'][source_type] += 1
        
       
        integration = metadata.get('integration', {})
        quality_score = integration.get('quality_score', 1.0)
        quality_bucket = self._get_quality_bucket(quality_score)
        
        if quality_bucket not in self.index_metadata['quality_distribution']:
            self.index_metadata['quality_distribution'][quality_bucket] = 0
        self.index_metadata['quality_distribution'][quality_bucket] += 1
        
        
        issues = integration.get('issues', [])
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            if issue_type not in self.index_metadata['issues_summary']:
                self.index_metadata['issues_summary'][issue_type] = 0
            self.index_metadata['issues_summary'][issue_type] += 1
        
      
        relationships = integration.get('relationships', [])
        for rel in relationships:
            rel_type = rel.get('type', 'unknown')
            if rel_type not in self.index_metadata['relationship_summary']:
                self.index_metadata['relationship_summary'][rel_type] = 0
            self.index_metadata['relationship_summary'][rel_type] += 1
        
       
        enrichment = metadata.get('enrichment', {})
        purpose = enrichment.get('purpose')
        if purpose:
            if purpose not in self.index_metadata['semantic_summary']:
                self.index_metadata['semantic_summary'][purpose] = 0
            self.index_metadata['semantic_summary'][purpose] += 1
    
    def _get_quality_bucket(self, quality_score: float) -> str:
        """Get quality bucket for score"""
        if quality_score >= 0.8:
            return 'high'
        elif quality_score >= 0.6:
            return 'medium'
        elif quality_score >= 0.4:
            return 'low'
        else:
            return 'very_low'
    
    def _generate_index_summary(self, original_documents: List[Dict[str, Any]], filtered_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive index summary"""
        summary = {
            'document_counts': {
                'total_input': len(original_documents),
                'filtered_accepted': len(filtered_documents),
                'skipped': len(self.index_metadata['documents_skipped']),
                'by_source_type': self.index_metadata['content_summary']
            },
            'quality_analysis': {
                'quality_distribution': self.index_metadata['quality_distribution'],
                'quality_threshold_used': self.quality_threshold,
                'filtering_enabled': self.enrichment_config['use_integration_filtering']
            },
            'issues_detected': {
                'total_issue_types': len(self.index_metadata['issues_summary']),
                'issues_by_type': self.index_metadata['issues_summary'],
                'high_severity_filtering': self.enrichment_config['skip_high_severity_issues']
            },
            'relationship_analysis': {
                'total_relationship_types': len(self.index_metadata['relationship_summary']),
                'relationships_by_type': self.index_metadata['relationship_summary'],
                'relationship_metadata_included': self.enrichment_config['include_relationship_metadata']
            },
            'semantic_analysis': {
                'purposes_detected': self.index_metadata['semantic_summary'],
                'semantic_enhancement_enabled': self.enrichment_config['use_semantic_enhancement']
            },
            'skipped_documents': {
                'count': len(self.index_metadata['documents_skipped']),
                'details': self.index_metadata['documents_skipped'][:10]  
            }
        }
        
        return summary
    
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
        hash_input = f"{content}_{metadata.get('file_path', '')}_{metadata.get('chunk_index', 0)}_{self.user_id}_{self.org_id}"
        content_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        source_type = metadata.get('source_type', 'doc')
        tenant_prefix = "demo" if self.demo_mode else self.org_id[:8]
        chunk_id = f"{tenant_prefix}_{source_type}_{content_hash}_{uuid.uuid4().hex[:8]}"
        
        return chunk_id
    
    def _chunk_exists(self, collection, chunk_id: str) -> bool:
        """Check if chunk already exists in collection"""
        try:
            result = collection.get(ids=[chunk_id])
            return len(result['ids']) > 0
        except:
            return False
    
    def get_user_documents(self, collection_type: str = "main", limit: int = 100) -> Dict[str, Any]:
        """Get documents for current user/org with enhanced filtering"""
        try:
            collection = self.collections.get(collection_type)
            if not collection:
                raise ValueError(f"Collection type '{collection_type}' not found")
            
            if self.demo_mode:
                where_filter = {"demo_mode": True}
            else:
                where_filter = {"org_id": self.org_id}
            
            results = collection.get(
                where=where_filter,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
         
            enriched_analysis = self._analyze_retrieved_documents(results.get("metadatas", []))
            
            return {
                "success": True,
                "documents": results.get("documents", []),
                "metadatas": results.get("metadatas", []),
                "count": len(results.get("documents", [])),
                "collection": collection_type,
                
                "enriched_analysis": enriched_analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "documents": [],
                "metadatas": [],
                "count": 0
            }
    
    def search_documents(
        self, 
        query: str, 
        collection_type: str = "main", 
        n_results: int = 10,
        quality_threshold: float = None
    ) -> Dict[str, Any]:
        """Enhanced search with quality filtering and enriched results"""
        try:
            collection = self.collections.get(collection_type)
            if not collection:
                raise ValueError(f"Collection type '{collection_type}' not found")
            
         
            if self.demo_mode:
                where_filter = {"demo_mode": True}
            else:
                where_filter = {"org_id": self.org_id}
            
          
            if quality_threshold is not None:
                where_filter["integration_quality"] = {"$gte": quality_threshold}
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            
            enhanced_results = self._enhance_search_results(results)
            
            return {
                "success": True,
                "query": query,
                "results": enhanced_results,
                "count": len(enhanced_results.get("documents", [])),
                "collection": collection_type,
                "quality_threshold": quality_threshold
            }
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": {
                    "documents": [],
                    "metadatas": [],
                    "distances": []
                },
                "count": 0
            }
    
    def _analyze_retrieved_documents(self, metadatas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze retrieved documents for enriched insights"""
        analysis = {
            'source_distribution': {},
            'quality_distribution': {},
            'purpose_distribution': {},
            'enriched_documents': 0,
            'average_quality': 0.0
        }
        
        quality_scores = []
        
        for metadata in metadatas:
           
            source_type = metadata.get('source_type', 'unknown')
            analysis['source_distribution'][source_type] = analysis['source_distribution'].get(source_type, 0) + 1
            
        
            quality_score = metadata.get('integration_quality', 1.0)
            quality_scores.append(quality_score)
            quality_bucket = self._get_quality_bucket(quality_score)
            analysis['quality_distribution'][quality_bucket] = analysis['quality_distribution'].get(quality_bucket, 0) + 1
            
          
            purpose = metadata.get('enriched_purpose', 'unknown')
            analysis['purpose_distribution'][purpose] = analysis['purpose_distribution'].get(purpose, 0) + 1
            
          
            if metadata.get('enriched_purpose') or metadata.get('llm_summary'):
                analysis['enriched_documents'] += 1
        
       
        if quality_scores:
            analysis['average_quality'] = sum(quality_scores) / len(quality_scores)
        
        return analysis
    
    def _enhance_search_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance search results with enriched metadata"""
        enhanced = {
            "documents": results.get("documents", [[]])[0],
            "metadatas": results.get("metadatas", [[]])[0],
            "distances": results.get("distances", [[]])[0]
        }
        
        
        if enhanced["metadatas"]:
            enhanced["enriched_analysis"] = self._analyze_retrieved_documents(enhanced["metadatas"])
        
        return enhanced
    
    def reindex_collection(self, collection_type: str = "main") -> Dict[str, Any]:
        """Completely rebuild a collection index"""
        try:
            logger.info(f"Starting reindex of {collection_type} collection for {'demo mode' if self.demo_mode else f'org {self.org_id}'}")
            
            collection_name = self.db_setup._get_collection_name(self.config['vector_store']['collection_name'])
            if collection_type != "main":
                collection_name = self.db_setup._get_collection_name(f"{self.config['vector_store']['collection_name']}_{collection_type}")
            
            success = self.db_setup.reset_collection(collection_name)
            if not success:
                raise Exception(f"Failed to reset collection {collection_name}")
            
            self.collections = self.db_setup.setup_collections()
            
            logger.info(f"Collection {collection_type} reindexed successfully")
            return {
                "success": True,
                "collection": collection_type,
                "user_id": self.user_id,
                "org_id": self.org_id,
                "message": "Collection reset and ready for new documents",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "enhanced_features_enabled": True
            }
            
        except Exception as e:
            logger.error(f"Error reindexing collection: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_indexing_stats(self) -> Dict[str, Any]:
        """Get comprehensive indexing statistics with enriched metadata"""
        stats = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id,
            "org_id": self.org_id,
            "demo_mode": self.demo_mode,
            "collections": {},
            "total_documents": 0,
            "total_chunks": 0,
            "config": {
                "chunk_size": self.config['vector_store']['chunk_size'],
                "chunk_overlap": self.config['vector_store']['chunk_overlap'],
                "embedding_model": self.config['vector_store']['embedding_model'],
                "quality_threshold": self.quality_threshold
            },
            
            "enriched_features": {
                "integration_filtering_enabled": self.enrichment_config['use_integration_filtering'],
                "semantic_enhancement_enabled": self.enrichment_config['use_semantic_enhancement'],
                "quality_threshold": self.quality_threshold,
                "high_severity_filtering": self.enrichment_config['skip_high_severity_issues']
            },
            "last_index_summary": self.index_metadata
        }
        
        try:
            for collection_name, collection in self.collections.items():
                if self.demo_mode:
                    where_filter = {"demo_mode": True}
                else:
                    where_filter = {"org_id": self.org_id}
                
                try:
                    
                    user_docs = collection.get(
                        where=where_filter, 
                        limit=1000,  
                        include=["metadatas"]
                    )
                    user_count = len(user_docs.get("documents", []))
                    total_count = collection.count()
                    
                    
                    enriched_analysis = self._analyze_retrieved_documents(user_docs.get("metadatas", []))
                    
                except Exception as e:
                    logger.debug(f"Error getting collection stats: {e}")
                    user_count = 0
                    total_count = collection.count()
                    enriched_analysis = {}
                
                metadata = collection.metadata or {}
                
                stats["collections"][collection_name] = {
                    "user_document_count": user_count,
                    "total_document_count": total_count,
                    "metadata": metadata,
                    "enriched_analysis": enriched_analysis
                }
                stats["total_chunks"] += user_count
            
            avg_chunks_per_doc = 3
            stats["estimated_documents"] = stats["total_chunks"] // avg_chunks_per_doc if stats["total_chunks"] > 0 else 0
            
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    async def build_index_from_sources(self, data_sources: List[str] = None) -> Dict[str, Any]:
        """Build index from configured data sources with enhanced processing"""
        if not data_sources:
            data_sources = ['codebase', 'documentation', 'slack', 'pr', 'ticket']
        
        results = {
            "success": True,
            "user_id": self.user_id,
            "org_id": self.org_id,
            "demo_mode": self.demo_mode,
            "sources_processed": [],
            "total_documents": 0,
            "total_chunks": 0,
            "errors": [],
            
            "enriched_processing": {
                "quality_filtering_enabled": self.enrichment_config['use_integration_filtering'],
                "semantic_enhancement_enabled": self.enrichment_config['use_semantic_enhancement'],
                "sources_with_enrichment": [],
                "total_documents_skipped": 0,
                "quality_distribution": {},
                "aggregated_index_summary": {}
            }
        }
        
        aggregated_summary = {
            'document_counts': {'total_input': 0, 'filtered_accepted': 0, 'skipped': 0},
            'quality_analysis': {'quality_distribution': {}},
            'issues_detected': {'issues_by_type': {}},
            'relationship_analysis': {'relationships_by_type': {}},
            'semantic_analysis': {'purposes_detected': {}}
        }
        
        try:
            for source in data_sources:
                try:
                    if source == 'codebase':
                        from data_sources.code_parser import CodeParser
                        parser = CodeParser(demo_mode=self.demo_mode)
                        documents = await parser.parse_codebase()
                        
                    elif source == 'documentation':
                        from data_sources.doc_ingestor import DocIngestor
                        ingestor = DocIngestor(demo_mode=self.demo_mode)
                        documents = await ingestor.ingest_docs()
                               
                    elif source == "slack":
                        from data_sources.slack_parser import SlackParser
                        parser = SlackParser(demo_mode=self.demo_mode)
                        documents = await parser.parse_export()

                    elif source == "pr":
                        from data_sources.pr_fetcher import PRFetcher
                        parser = PRFetcher(demo_mode=self.demo_mode)
                        documents = await parser.fetch_prs()

                    elif source == "ticket":
                        from data_sources.ticket_fetcher import TicketFetcher
                        parser = TicketFetcher(demo_mode=self.demo_mode)
                        documents = await parser.fetch_tickets()

                    else:
                        logger.warning(f"Unknown data source: {source}")
                        continue
                    
                    
                    has_enrichment = any(
                        doc.get('metadata', {}).get('enrichment') or 
                        doc.get('metadata', {}).get('integration')
                        for doc in documents
                    )
                    
                    if has_enrichment:
                        results["enriched_processing"]["sources_with_enrichment"].append(source)
                    
                    result = self.add_documents(documents, source)
                    
                    if result['success']:
                        results["sources_processed"].append(source)
                        results["total_documents"] += result['documents_processed']
                        results["total_chunks"] += result['chunks_created']
                        
                    
                        enriched_info = result.get('enriched_indexing', {})
                        if enriched_info:
                            results["enriched_processing"]["total_documents_skipped"] += enriched_info.get('documents_skipped', 0)
                            
                           
                            index_summary = enriched_info.get('index_summary', {})
                            if index_summary:
                                self._aggregate_index_summaries(aggregated_summary, index_summary)
                    else:
                        results["errors"].append(f"{source}: {result['error']}")
                        
                except Exception as e:
                    logger.error(f"Error processing {source}: {str(e)}")
                    results["errors"].append(f"{source}: {str(e)}")
            
          
            results["enriched_processing"]["aggregated_index_summary"] = aggregated_summary
            
            if results["errors"]:
                results["success"] = False
            
        except Exception as e:
            results["success"] = False
            results["errors"].append(f"General error: {str(e)}")
        
        return results
    
    def _aggregate_index_summaries(self, aggregated: Dict[str, Any], source_summary: Dict[str, Any]):
        """Aggregate index summaries from multiple sources"""
        
        doc_counts = source_summary.get('document_counts', {})
        aggregated['document_counts']['total_input'] += doc_counts.get('total_input', 0)
        aggregated['document_counts']['filtered_accepted'] += doc_counts.get('filtered_accepted', 0)
        aggregated['document_counts']['skipped'] += doc_counts.get('skipped', 0)
        
        
        quality_dist = source_summary.get('quality_analysis', {}).get('quality_distribution', {})
        for quality_level, count in quality_dist.items():
            aggregated['quality_analysis']['quality_distribution'][quality_level] = \
                aggregated['quality_analysis']['quality_distribution'].get(quality_level, 0) + count
        
        
        issues = source_summary.get('issues_detected', {}).get('issues_by_type', {})
        for issue_type, count in issues.items():
            aggregated['issues_detected']['issues_by_type'][issue_type] = \
                aggregated['issues_detected']['issues_by_type'].get(issue_type, 0) + count
        
       
        relationships = source_summary.get('relationship_analysis', {}).get('relationships_by_type', {})
        for rel_type, count in relationships.items():
            aggregated['relationship_analysis']['relationships_by_type'][rel_type] = \
                aggregated['relationship_analysis']['relationships_by_type'].get(rel_type, 0) + count
        
        
        purposes = source_summary.get('semantic_analysis', {}).get('purposes_detected', {})
        for purpose, count in purposes.items():
            aggregated['semantic_analysis']['purposes_detected'][purpose] = \
                aggregated['semantic_analysis']['purposes_detected'].get(purpose, 0) + count


def quick_index(documents: List[Dict], collection_type: str = "main", user_id: str = None, org_id: str = None) -> Dict[str, Any]:
    """Quick indexing function for simple use cases with enhanced processing"""
    builder = IndexBuilder(user_id=user_id, org_id=org_id)
    return builder.add_documents(documents, collection_type)

def rebuild_index(collection_type: str = "main", user_id: str = None, org_id: str = None) -> Dict[str, Any]:
    """Quickly rebuild an index"""
    builder = IndexBuilder(user_id=user_id, org_id=org_id)
    return builder.reindex_collection(collection_type)

def search_user_docs(query: str, collection_type: str = "main", user_id: str = None, org_id: str = None, n_results: int = 10, quality_threshold: float = None) -> Dict[str, Any]:
    """Quick search function with enhanced filtering"""
    builder = IndexBuilder(user_id=user_id, org_id=org_id)
    return builder.search_documents(query, collection_type, n_results, quality_threshold)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        user_id = sys.argv[2] if len(sys.argv) > 2 else None
        org_id = sys.argv[3] if len(sys.argv) > 3 else None
        
        builder = IndexBuilder(user_id=user_id, org_id=org_id)
        
        if command == "stats":
            stats = builder.get_indexing_stats()
            print("Enhanced Indexing Statistics:")
            print(json.dumps(stats, indent=2))
            
        elif command == "reindex":
            collection_type = sys.argv[4] if len(sys.argv) > 4 else "main"
            result = builder.reindex_collection(collection_type)
            print(f"Reindex result: {result}")
            
        elif command == "build":
            sources = sys.argv[4:] if len(sys.argv) > 4 else None
            result = asyncio.run(builder.build_index_from_sources(sources))
            print(f"Enhanced build result:")
            print(json.dumps(result, indent=2))
            
        elif command == "search":
            query = sys.argv[4] if len(sys.argv) > 4 else "test"
            collection_type = sys.argv[5] if len(sys.argv) > 5 else "main"
            quality_threshold = float(sys.argv[6]) if len(sys.argv) > 6 else None
            result = builder.search_documents(query, collection_type, n_results=10, quality_threshold=quality_threshold)
            print(f"Enhanced search result:")
            print(json.dumps(result, indent=2))
            
        else:
            print("Available commands: stats, reindex [collection], build [sources...], search [query] [collection] [quality_threshold]")
            print("Enhanced features:")
            print("  - Integration quality filtering")
            print("  - Semantic enhancement")
            print("  - Issue detection and filtering")
            print("  - Relationship metadata inclusion")
            print("  - Comprehensive index summaries")
    else:
        print("Usage: python index_builder.py [stats|reindex|build|search] [user_id] [org_id] [args...]")
        print("Enhanced Index Builder with:")
        print("  ✓ Integration-aware filtering")
        print("  ✓ Semantic field selection")
        print("  ✓ Quality-based document filtering")
        print("  ✓ Issue severity filtering")
        print("  ✓ Enriched metadata tracking")
        print("  ✓ Comprehensive index summaries")