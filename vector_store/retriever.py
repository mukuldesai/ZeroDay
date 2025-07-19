import os
import yaml
from typing import List, Dict, Any, Optional, Union
from loguru import logger
from datetime import datetime
import numpy as np
from vector_store.chromadb_setup import ChromaDBSetup

class Retriever:
    """
    Advanced Retriever: Intelligent context retrieval for all agents
    Enhanced with enriched metadata integration and semantic filtering
    """
    
    def __init__(self, config_path: str = None, user_id: str = None, org_id: str = None):
        self.config = self._load_config(config_path)
        self.user_id = user_id or "demo_user"
        self.org_id = org_id or "demo_org"
        self.demo_mode = self.user_id == "demo_user"
        self.db_setup = ChromaDBSetup(config_path, user_id, org_id)
        self.db_setup.initialize_client()
        self.collections = self.db_setup.setup_collections()
        
        
        self.default_quality_threshold = 0.5
        self.high_severity_issues = ["critical", "blocking", "error"]
        self.relationship_boosts = {
            "explains": 1.2,
            "supports": 1.1,
            "tests": 1.15,
            "references": 1.05,
            "implements": 1.1,
            "depends_on": 1.0
        }
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_user_filter(self) -> Dict[str, Any]:
        """Get base filter for user/org isolation"""
        if self.demo_mode:
            return {"demo_mode": True}
        else:
            return {"org_id": self.org_id}
    

    async def retrieve(
        self,
        query: str,
        collection_types: List[str] = None,
        n_results: int = None,
        filters: Dict[str, Any] = None,
        rerank: bool = True,
        include_metadata: bool = True,
        # Enhanced filtering options - TEMPORARILY DISABLED
        filter_by_purpose: List[str] = None,
        min_quality_score: float = None,
        boost_topic: str = None,
        include_enriched_analysis: bool = False
    ) -> Dict[str, Any]:
        """
        IMMEDIATE FIX: Simplified retrieval without enhanced filtering
        """
        try:
            if not n_results:
                n_results = self.config['agents']['knowledge']['max_results']
            
            if not collection_types:
                collection_types = ['main'] 
            
            # TEMPORARY: Use only basic user filter, skip enhanced filters
            user_filter = self._get_user_filter()
            if filters:
                user_filter.update(filters)
            # Skip enhanced filtering for now
            # enhanced_filters = self._build_enhanced_filters(...)
            
            logger.info(f"Basic retrieval from collections: {collection_types}")
            
            all_results = []
            for collection_type in collection_types:
                if collection_type in self.collections:
                    # Use basic search without enhanced features
                    results = await self._basic_search_collection(
                        query=query,
                        collection=self.collections[collection_type],
                        collection_type=collection_type,
                        n_results=n_results,
                        filters=user_filter  # Use basic filters only
                    )
                    all_results.extend(results)
        
            if rerank and all_results:
                # Use basic reranking without enhanced features
                all_results = self._basic_rerank_results(query, all_results)
            
            final_results = all_results[:n_results]
            relevance_stats = self._calculate_relevance_stats(final_results)
            
            response = {
                "results": final_results,
                "query": query,
                "collections_searched": collection_types,
                "total_results": len(final_results),
                "relevance_stats": relevance_stats,
                "user_id": self.user_id,
                "org_id": self.org_id,
                "demo_mode": self.demo_mode,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": True,
                "mode": "basic"  # Indicate this is basic mode
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error in basic retrieval: {str(e)}")
            return {
                "results": [],
                "query": query,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    # REPLACE THIS METHOD IN retriever.py

    def _safe_text_decode(self, content) -> str:
        """ENHANCED: Ultra-robust text cleaning for Windows encoding issues"""
        if not content:
            return ""
        
        try:
            # Step 1: Handle different input types
            if isinstance(content, bytes):
                # Try multiple encodings for bytes
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'ascii', 'utf-16']:
                    try:
                        content = content.decode(encoding, errors='ignore')
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue
            
            # Convert to string if not already
            content = str(content)
            
            # Step 2: Remove ALL control characters and problematic bytes
            import re
            # Remove control characters except newlines, tabs, carriage returns
            content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
            
            # Step 3: Handle specific Windows problematic characters
            problematic_replacements = {
                '\x8f': '',      # The specific byte causing issues
                '\x9f': '',
                '\x81': '',
                '\x9d': '',
                '\x8d': '',
                '\x90': '',
                '\x9c': '',
                # Smart quotes and similar
                '\u2018': "'",   # Left single quotation mark
                '\u2019': "'",   # Right single quotation mark  
                '\u201c': '"',   # Left double quotation mark
                '\u201d': '"',   # Right double quotation mark
                '\u2013': '-',   # En dash
                '\u2014': '-',   # Em dash
                '\u2026': '...',  # Horizontal ellipsis
            }
            
            for char, replacement in problematic_replacements.items():
                content = content.replace(char, replacement)
            
            # Step 4: Process in chunks to avoid large corrupt sections
            chunk_size = 1000
            cleaned_chunks = []
            
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                try:
                    # Test if chunk is safe
                    chunk.encode('utf-8', errors='strict')
                    cleaned_chunks.append(chunk)
                except UnicodeEncodeError:
                    # Clean chunk character by character
                    safe_chunk = ""
                    for char in chunk:
                        try:
                            char.encode('utf-8', errors='strict')
                            if 32 <= ord(char) <= 126 or char in '\n\r\t':
                                safe_chunk += char
                        except:
                            pass  # Skip problematic chars
                    cleaned_chunks.append(safe_chunk)
            
            content = ''.join(cleaned_chunks)
            
            # Step 5: Final validation and length limit
            if len(content) > 8000:
                content = content[:8000] + "..."
            
            # Final test encode/decode
            content = content.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            
            return content.strip()
            
        except Exception as e:
            # Ultra-safe fallback: ASCII only
            try:
                safe_fallback = ''.join(char for char in str(content) if 32 <= ord(char) <= 126)
                return safe_fallback[:500] if safe_fallback else "Content unavailable"
            except:
                return "Content processing failed"

    # ADD THIS METHOD TO THE Retriever CLASS in retriever.py

    def _safe_process_chromadb_results(self, results):
        """Safely process ChromaDB results to prevent encoding errors"""
        if not results or not results.get('documents'):
            return []
        
        safe_results = []
        documents = results.get('documents', [[]])
        metadatas = results.get('metadatas', [[]])
        distances = results.get('distances', [[]])
        
        if not documents or not documents[0]:
            return []
        
        for i in range(len(documents[0])):
            try:
                # Safely extract and clean content
                content = documents[0][i] if i < len(documents[0]) else ""
                content = self._safe_text_decode(content)
                
                # Safely extract metadata
                metadata = metadatas[0][i] if (metadatas and metadatas[0] and i < len(metadatas[0])) else {}
                
                # Clean metadata strings
                cleaned_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, str):
                        cleaned_metadata[key] = self._safe_text_decode(value)
                    else:
                        cleaned_metadata[key] = value
                
                # Safely extract distance
                distance = distances[0][i] if (distances and distances[0] and i < len(distances[0])) else 1.0
                
                safe_results.append({
                    'content': content,
                    'metadata': cleaned_metadata,
                    'distance': distance,
                    'relevance_score': 1.0 - distance
                })
                
            except Exception as e:
                logger.warning(f"Error processing ChromaDB result {i}: {e}")
                # Add safe fallback result
                safe_results.append({
                    'content': f"Error processing result {i}",
                    'metadata': {'error': str(e)},
                    'distance': 1.0,
                    'relevance_score': 0.0
                })
        
        return safe_results

    async def _basic_search_collection(
        self,
        query: str,
        collection,
        collection_type: str,
        n_results: int,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Basic collection search with ENHANCED encoding safety"""
        try:
            # Use only simple filters
            where_clause = None
            if filters:
                # Only use basic string/int filters
                simple_filters = {}
                for key, value in filters.items():
                    if isinstance(value, (str, int, float, bool)):
                        simple_filters[key] = value
                
                if simple_filters:
                    where_clause = simple_filters
        
            # SAFE: Query with error handling
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results, 
                    where=where_clause,
                    include=['documents', 'metadatas', 'distances']
                )
            except Exception as query_error:
                logger.error(f"ChromaDB query failed for {collection_type}: {query_error}")
                return []
            
            # ENHANCED: Use safe processing method
            formatted_results = self._safe_process_chromadb_results(results)
            
            # Add collection type to all results
            for result in formatted_results:
                result['collection_type'] = collection_type
                result['metadata']['collection_type'] = collection_type
            
            logger.debug(f"Found {len(formatted_results)} results in {collection_type}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in basic search for {collection_type}: {str(e)}")
            return []

    def _basic_rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Basic reranking without enhanced features"""
        try:
            # Simple deduplication and sorting by relevance score
            seen_content = set()
            deduplicated = []
            
            for result in results:
                content_hash = hash(result['content'][:100])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    deduplicated.append(result)
            
            # Sort by relevance score
            ranked_results = sorted(deduplicated, key=lambda x: x['relevance_score'], reverse=True)
            
            logger.debug(f"Basic re-ranking: {len(results)} -> {len(ranked_results)} results")
            return ranked_results
            
        except Exception as e:
            logger.error(f"Error in basic re-ranking: {str(e)}")
            return results
    
    def _build_enhanced_filters(
        self,
        base_filters: Dict[str, Any],
        user_filter: Dict[str, Any],
        filter_by_purpose: List[str] = None,
        min_quality_score: float = None
    ) -> Dict[str, Any]:
        """Build enhanced filters with safe fallbacks"""
        filters = user_filter.copy()
        
        if base_filters:
            filters.update(base_filters)
        
        # Temporarily disable complex filters to fix the immediate issue
        # TODO: Re-enable after ChromaDB syntax is fixed
        
        # Add quality score filtering (simple approach)
        # if min_quality_score is not None:
        #     filters["integration.quality_score"] = {"$gte": min_quality_score}
        
        # Add purpose filtering (simple approach)
        if filter_by_purpose:
            # Use simple equality for now instead of $in
            if len(filter_by_purpose) == 1:
                filters["enrichment.purpose"] = filter_by_purpose[0]
            # Skip multiple purpose filtering for now
        
        # Skip issue severity filtering for now
        # filters["integration.issues.severity"] = {
        #     "$nin": self.high_severity_issues
        # }
        
        return filters
   
    
    async def _search_collection(
        self,
        query: str,
        collection,
        collection_type: str,
        n_results: int,
        filters: Dict[str, Any] = None,
        boost_topic: str = None
    ) -> List[Dict[str, Any]]:
        """Enhanced collection search with encoding safety"""
        try:
            # Safe query processing
            query = self._safe_text_decode(query)
            
            where_clause = self._build_where_clause(filters) if filters else None
            logger.debug(f"ChromaDB where clause for {collection_type}: {where_clause}")
        
            results = collection.query(
                query_texts=[query],
                n_results=n_results * 2, 
                where=where_clause,
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    try:
                        # Safe content processing
                        content = self._safe_text_decode(results['documents'][0][i])
                        metadata = results['metadatas'][0][i] if results['metadatas'][0] else {}
                        
                        # Clean metadata too
                        cleaned_metadata = {}
                        for key, value in metadata.items():
                            if isinstance(value, str):
                                cleaned_metadata[key] = self._safe_text_decode(value)
                            else:
                                cleaned_metadata[key] = value
                        
                        result = {
                            'content': content,
                            'metadata': cleaned_metadata,
                            'distance': results['distances'][0][i] if results['distances'][0] else 1.0,
                            'collection_type': collection_type,
                            'relevance_score': 1.0 - results['distances'][0][i] if results['distances'][0] else 0.0
                        }
                        
                        # Apply semantic and integration boosts safely
                        try:
                            result = self._apply_semantic_boosts(result, query, boost_topic)
                        except Exception as boost_error:
                            logger.warning(f"Error applying semantic boosts: {boost_error}")
                            # Continue without boosts
                        
                        result['metadata']['collection_type'] = collection_type
                        formatted_results.append(result)
                        
                    except Exception as item_error:
                        logger.warning(f"Error processing search result item: {item_error}")
                        continue
            
            logger.debug(f"Found {len(formatted_results)} results in {collection_type}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching collection {collection_type}: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Filters: {filters}")
            return []

    def _apply_semantic_boosts(
        self, 
        result: Dict[str, Any], 
        query: str, 
        boost_topic: str = None
    ) -> Dict[str, Any]:
        """Apply semantic boosts based on enriched metadata"""
        metadata = result.get('metadata', {})
        base_score = result.get('relevance_score', 0.0)
        
        
        quality_boost = self._get_integration_quality_boost(metadata)
        
     
        semantic_boost = self._get_semantic_matching_boost(metadata, query)
        
        
        purpose_boost = self._get_purpose_alignment_boost(metadata, query)
        
        
        relationship_boost = self._get_relationship_boost(metadata)
        
     
        topic_boost = self._get_topic_boost(metadata, boost_topic) if boost_topic else 1.0
        
        
        issue_penalty = self._get_issue_penalty(metadata)
        
        
        enhanced_score = (
            base_score * 
            quality_boost * 
            semantic_boost * 
            purpose_boost * 
            relationship_boost * 
            topic_boost * 
            issue_penalty
        )
        
        result['enhanced_relevance_score'] = min(1.0, max(0.0, enhanced_score))
        result['boost_factors'] = {
            'quality': quality_boost,
            'semantic': semantic_boost,
            'purpose': purpose_boost,
            'relationship': relationship_boost,
            'topic': topic_boost,
            'issue_penalty': issue_penalty
        }
        
        return result
    
    def _get_integration_quality_boost(self, metadata: Dict[str, Any]) -> float:
        """Boost based on integration quality score"""
        integration = metadata.get('integration', {})
        quality_score = integration.get('quality_score', 0.5)
        
        if quality_score > 0.8:
            return 1.2
        elif quality_score > 0.6:
            return 1.1
        elif quality_score > 0.4:
            return 1.0
        else:
            return 0.9
    
    def _get_semantic_matching_boost(self, metadata: Dict[str, Any], query: str) -> float:
        """Boost based on semantic metadata matching"""
        semantic = metadata.get('semantic', {})
        query_tokens = set(query.lower().split())
        
        boost = 1.0
        
        
        key_entities = semantic.get('key_entities', [])
        entity_matches = sum(1 for entity in key_entities if entity.lower() in query_tokens)
        if entity_matches > 0:
            boost *= 1.0 + (entity_matches * 0.1)
        
        
        primary_actions = semantic.get('primary_actions', [])
        action_matches = sum(1 for action in primary_actions if action.lower() in query_tokens)
        if action_matches > 0:
            boost *= 1.0 + (action_matches * 0.15)
        
       
        topics = semantic.get('topics', [])
        topic_matches = sum(1 for topic in topics if topic.lower() in query_tokens)
        if topic_matches > 0:
            boost *= 1.0 + (topic_matches * 0.1)
        
        return min(1.5, boost)
    
    def _get_purpose_alignment_boost(self, metadata: Dict[str, Any], query: str) -> float:
        """Boost based on purpose alignment with query"""
        enrichment = metadata.get('enrichment', {})
        purpose = enrichment.get('purpose', '').lower()
        query_lower = query.lower()
        
        
        purpose_patterns = {
            'api_endpoint': ['api', 'endpoint', 'request', 'response'],
            'testing': ['test', 'testing', 'spec', 'unit', 'integration'],
            'documentation': ['doc', 'guide', 'help', 'how', 'usage'],
            'configuration': ['config', 'setup', 'settings', 'environment'],
            'troubleshooting': ['error', 'issue', 'problem', 'debug', 'fix'],
            'implementation': ['implement', 'create', 'build', 'develop']
        }
        
        for pattern_purpose, keywords in purpose_patterns.items():
            if purpose == pattern_purpose and any(keyword in query_lower for keyword in keywords):
                return 1.3
        
        return 1.0
    
    def _get_relationship_boost(self, metadata: Dict[str, Any]) -> float:
        """Boost based on relationship types"""
        integration = metadata.get('integration', {})
        relationships = integration.get('relationships', [])
        
        boost = 1.0
        for rel in relationships:
            rel_type = rel.get('type', '')
            if rel_type in self.relationship_boosts:
                boost *= self.relationship_boosts[rel_type]
        
        return min(1.5, boost)
    
    def _get_topic_boost(self, metadata: Dict[str, Any], boost_topic: str) -> float:
        """Boost based on topic relevance"""
        semantic = metadata.get('semantic', {})
        topics = semantic.get('topics', [])
        
        if boost_topic.lower() in [topic.lower() for topic in topics]:
            return 1.4
        
      
        key_entities = semantic.get('key_entities', [])
        primary_actions = semantic.get('primary_actions', [])
        
        if (boost_topic.lower() in [entity.lower() for entity in key_entities] or
            boost_topic.lower() in [action.lower() for action in primary_actions]):
            return 1.2
        
        return 1.0
    
    def _get_issue_penalty(self, metadata: Dict[str, Any]) -> float:
        """Apply penalty based on integration issues"""
        integration = metadata.get('integration', {})
        issues = integration.get('issues', [])
        
        if not issues:
            return 1.0
        
        penalty = 1.0
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity in self.high_severity_issues:
                penalty *= 0.7
            elif severity == 'medium':
                penalty *= 0.9
        
        return max(0.3, penalty)
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified where clause building for immediate fix"""
        conditions = []
        
        for key, value in filters.items():
            if isinstance(value, list):
                
                if value:
                    conditions.append({key: value[0]})
            elif isinstance(value, dict):
                if 'min' in value:
                    conditions.append({key: value['min']})
                elif 'max' in value:
                    conditions.append({key: value['max']})
                else:
                    continue
            else:
                conditions.append({key: value})
        

        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return conditions[0]
        else:
            return {}

    def _rerank_results_enhanced(
        self, 
        query: str, 
        results: List[Dict[str, Any]], 
        boost_topic: str = None
    ) -> List[Dict[str, Any]]:
        """Enhanced re-ranking using enriched metadata"""
        try:
            deduplicated = self._deduplicate_results(results)
            
            for result in deduplicated:
               
                if 'enhanced_relevance_score' in result:
                    result['final_score'] = result['enhanced_relevance_score']
                else:
                    result['final_score'] = self._calculate_final_score(query, result)
            
            ranked_results = sorted(deduplicated, key=lambda x: x['final_score'], reverse=True)
            
            logger.debug(f"Enhanced re-ranking: {len(results)} -> {len(ranked_results)} results")
            return ranked_results
            
        except Exception as e:
            logger.error(f"Error in enhanced re-ranking: {str(e)}")
            return results
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar results"""
        deduplicated = []
        seen_content = set()
        
        for result in results:
            content = result['content']
            content_hash = hash(content[:200])  
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                deduplicated.append(result)
        
        return deduplicated
    
    def _calculate_final_score(self, query: str, result: Dict[str, Any]) -> float:
        """Calculate final ranking score using multiple signals (legacy fallback)"""
        base_score = result.get('relevance_score', 0.0)
        metadata = result.get('metadata', {})
        
        collection_boost = self._get_collection_boost(result.get('collection_type', 'main'))
        recency_boost = self._get_recency_boost(metadata.get('created_at'))
        source_boost = self._get_source_type_boost(metadata.get('source_type'))
        length_penalty = self._get_length_penalty(result.get('content', ''))
     
        final_score = (
            base_score * 
            collection_boost * 
            recency_boost * 
            source_boost * 
            length_penalty
        )
        
        return min(1.0, max(0.0, final_score))
    
    def _get_collection_boost(self, collection_type: str) -> float:
        """Boost results from certain collections"""
        boosts = {
            'code': 1.1,        
            'documentation': 1.0,
            'pull_requests': 0.9,
            'slack_messages': 0.8,
            'tickets': 0.85,
            'main': 1.0
        }
        return boosts.get(collection_type, 1.0)
    
    def _get_recency_boost(self, created_at: str = None) -> float:
        """Boost more recent content"""
        if not created_at:
            return 1.0
        
        try:
            from dateutil.parser import parse
            created_date = parse(created_at)
            now = datetime.now(created_date.tzinfo) if created_date.tzinfo else datetime.now()
            days_old = (now - created_date).days
            
            if days_old < 7:
                return 1.1      
            elif days_old < 30:
                return 1.05     
            elif days_old < 90:
                return 1.0      
            else:
                return 0.95     
                
        except:
            return 1.0
    
    def _get_source_type_boost(self, source_type: str = None) -> float:
        """Boost results from certain source types"""
        boosts = {
            'documentation': 1.1,   
            'code': 1.0,
            'pr_description': 1.05,
            'slack': 0.9,           
            'ticket': 0.95,
            'comment': 0.85
        }
        return boosts.get(source_type, 1.0)
    
    def _get_length_penalty(self, content: str) -> float:
        """Slight penalty for very short or very long content"""
        length = len(content)
        
        if length < 50:
            return 0.9      
        elif length > 2000:
            return 0.95     
        else:
            return 1.0
    
    def _generate_enriched_analysis(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate enriched analysis of results"""
        if not results:
            return {
                "metadata_summary": {
                    "average_quality": 0.0,
                    "top_purposes": [],
                    "relationships_found": []
                }
            }
        
        quality_scores = []
        purposes = []
        relationships = []
        
        for result in results:
            metadata = result.get('metadata', {})
            
           
            integration = metadata.get('integration', {})
            quality_score = integration.get('quality_score')
            if quality_score is not None:
                quality_scores.append(quality_score)
            
           
            enrichment = metadata.get('enrichment', {})
            purpose = enrichment.get('purpose')
            if purpose:
                purposes.append(purpose)
            
            
            relationships_list = integration.get('relationships', [])
            for rel in relationships_list:
                rel_type = rel.get('type')
                if rel_type:
                    relationships.append(rel_type)
        
     
        avg_quality = np.mean(quality_scores) if quality_scores else 0.0
        
       
        from collections import Counter
        purpose_counts = Counter(purposes)
        top_purposes = [purpose for purpose, count in purpose_counts.most_common(3)]
        
       
        unique_relationships = list(set(relationships))
        
        return {
            "metadata_summary": {
                "average_quality": round(avg_quality, 3),
                "top_purposes": top_purposes,
                "relationships_found": unique_relationships[:5], 
                "quality_distribution": {
                    "high": len([q for q in quality_scores if q > 0.7]),
                    "medium": len([q for q in quality_scores if 0.4 <= q <= 0.7]),
                    "low": len([q for q in quality_scores if q < 0.4])
                },
                "purpose_distribution": dict(purpose_counts.most_common(5))
            }
        }
    
    def _calculate_relevance_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics about result relevance"""
        if not results:
            return {"avg_score": 0.0, "min_score": 0.0, "max_score": 0.0, "score_distribution": {}}
        
       
        scores = []
        for r in results:
            score = r.get('enhanced_relevance_score', r.get('final_score', r.get('relevance_score', 0.0)))
            scores.append(score)
        
        high_relevance = len([s for s in scores if s > 0.8])
        medium_relevance = len([s for s in scores if 0.5 < s <= 0.8])
        low_relevance = len([s for s in scores if s <= 0.5])
        
        return {
            "avg_score": round(np.mean(scores), 3),
            "min_score": round(min(scores), 3),
            "max_score": round(max(scores), 3),
            "score_distribution": {
                "high": high_relevance,
                "medium": medium_relevance, 
                "low": low_relevance
            }
        }
    
    async def retrieve_by_source(
        self,
        source_path: str,
        collection_types: List[str] = None,
        n_results: int = 20
    ) -> Dict[str, Any]:
        """Retrieve all chunks from a specific source file or path"""
        user_filter = self._get_user_filter()
        user_filter["file_path"] = source_path
        
        return await self.retrieve(
            query="",  
            collection_types=collection_types,
            n_results=n_results,
            filters=user_filter,
            rerank=False  
        )
    
    async def retrieve_similar_to_content(
        self,
        content: str,
        collection_types: List[str] = None,
        n_results: int = 10,
        exclude_exact_match: bool = True
    ) -> Dict[str, Any]:
        """Find content similar to provided text"""
        results = await self.retrieve(
            query=content[:500],  
            collection_types=collection_types,
            n_results=n_results * 2 if exclude_exact_match else n_results
        )
        
        if exclude_exact_match and results['success']:
            filtered_results = []
            for result in results['results']:
                if result['content'].strip() != content.strip():
                    filtered_results.append(result)
            
            results['results'] = filtered_results[:n_results]
            results['total_results'] = len(filtered_results)
        
        return results
    
    async def get_user_context(self, limit: int = 50) -> Dict[str, Any]:
        """Get recent user activity and context"""
        try:
            user_filter = self._get_user_filter()
            
            recent_docs = []
            for collection_type, collection in self.collections.items():
                try:
                    results = collection.get(
                        where=user_filter,
                        limit=limit // len(self.collections),
                        include=['metadatas']
                    )
                    
                    for metadata in results.get('metadatas', []):
                        if metadata:
                            metadata['collection_type'] = collection_type
                            recent_docs.append(metadata)
                
                except Exception as e:
                    logger.debug(f"Error getting context from {collection_type}: {str(e)}")
                    continue
            
            recent_docs.sort(key=lambda x: x.get('indexed_at', ''), reverse=True)
            
            context_summary = {
                "recent_activity": recent_docs[:limit],
                "activity_count": len(recent_docs),
                "collections_active": list(set([doc.get('collection_type') for doc in recent_docs if doc.get('collection_type')])),
                "source_types": list(set([doc.get('source_type') for doc in recent_docs if doc.get('source_type')])),
                "user_id": self.user_id,
                "org_id": self.org_id,
                "demo_mode": self.demo_mode
            }
            
            return context_summary
            
        except Exception as e:
            logger.error(f"Error getting user context: {str(e)}")
            return {
                "recent_activity": [],
                "activity_count": 0,
                "collections_active": [],
                "source_types": [],
                "error": str(e)
            }
    
    async def get_retriever_stats(self) -> Dict[str, Any]:
        """Get comprehensive retriever statistics"""
        stats = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id,
            "org_id": self.org_id,
            "demo_mode": self.demo_mode,
            "collections": {},
            "config": {
                "distance_threshold": self.config['vector_store']['distance_threshold'],
                "max_results": self.config['agents']['knowledge']['max_results'],
                "default_quality_threshold": self.default_quality_threshold
            }
        }
        
        try:
            user_filter = self._get_user_filter()
            
            for collection_name, collection in self.collections.items():
                total_count = collection.count()
                
                try:
                    user_docs = collection.get(where=user_filter, limit=1)
                    user_count = len(user_docs.get('documents', []))
                except:
                    user_count = 0
                
                if total_count > 0:
                    try:
                        sample = collection.get(where=user_filter, limit=5, include=['metadatas'])
                        
                        source_types = set()
                        file_extensions = set()
                        purposes = set()
                        avg_quality = 0.0
                        quality_count = 0
                        
                        for metadata in sample.get('metadatas', []):
                            if metadata:
                                source_types.add(metadata.get('source_type', 'unknown'))
                                file_path = metadata.get('file_path', '')
                                if '.' in file_path:
                                    file_extensions.add(file_path.split('.')[-1])
                                
                            
                                enrichment = metadata.get('enrichment', {})
                                purpose = enrichment.get('purpose')
                                if purpose:
                                    purposes.add(purpose)
                                
                                integration = metadata.get('integration', {})
                                quality_score = integration.get('quality_score')
                                if quality_score is not None:
                                    avg_quality += quality_score
                                    quality_count += 1
                        
                        stats["collections"][collection_name] = {
                            "user_document_count": user_count,
                            "total_document_count": total_count,
                            "source_types": list(source_types),
                            "file_extensions": list(file_extensions),
                            "purposes": list(purposes),
                            "avg_quality_score": round(avg_quality / quality_count, 3) if quality_count > 0 else 0.0
                        }
                    except Exception as e:
                        stats["collections"][collection_name] = {
                            "user_document_count": user_count,
                            "total_document_count": total_count,
                            "source_types": [],
                            "file_extensions": [],
                            "purposes": [],
                            "avg_quality_score": 0.0,
                            "error": str(e)
                        }
                else:
                    stats["collections"][collection_name] = {
                        "user_document_count": 0,
                        "total_document_count": 0,
                        "source_types": [],
                        "file_extensions": [],
                        "purposes": [],
                        "avg_quality_score": 0.0
                    }
        
        except Exception as e:
            stats["error"] = str(e)
        
        return stats


class ContextualRetriever(Retriever):
    """
    Enhanced retriever with contextual understanding for different agent types
    Integrates enriched metadata for better agent-specific results
    """
    
    def __init__(self, config_path: str = None, user_id: str = None, org_id: str = None):
        super().__init__(config_path, user_id, org_id)
        self.problem_patterns = {
            "authentication_error": ["auth", "login", "token", "unauthorized", "403", "401"],
            "database_connection": ["database", "db", "connection", "timeout", "pool"],
            "build_failure": ["build", "compile", "webpack", "npm", "yarn", "error"],
            "deployment_issue": ["deploy", "production", "server", "docker", "k8s"],
            "performance_problem": ["slow", "performance", "memory", "cpu", "optimization"]
        }
        
        
        self.agent_purposes = {
            "knowledge": ["api_endpoint", "documentation", "implementation", "configuration"],
            "guide": ["documentation", "tutorial", "guide", "learning"],
            "mentor": ["troubleshooting", "debugging", "solution", "fix"],
            "task": ["implementation", "feature", "bug_fix", "testing"]
        }
    
    async def retrieve_for_knowledge_agent(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimized retrieval for knowledge agent queries with enriched metadata"""
        collection_types = self._infer_collection_types(query)
        filters = self._build_context_filters(context) if context else None
        
       
        filter_by_purpose = self.agent_purposes.get("knowledge")
        
        
        boost_topic = self._extract_primary_topic(query)
        
        return await self.retrieve(
            query=query,
            collection_types=collection_types,
            filters=filters,
            filter_by_purpose=filter_by_purpose,
            boost_topic=boost_topic,
            n_results=self.config['agents']['knowledge']['max_results'],
            rerank=True,
            include_enriched_analysis=True
        )
    
    async def retrieve_for_guide_agent(
        self,
        user_role: str,
        user_id: Optional[str] = None,
        learning_goal: str = None,
        experience_level: str = "beginner"
    ) -> Dict[str, Any]:
        """Specialized retrieval for learning path generation with enriched metadata"""
        collection_types = ['documentation', 'main']
        
        query_parts = [user_role]
        if learning_goal:
            query_parts.append(learning_goal)
        
        query = " ".join(query_parts)
        
       
        filters = {
            "source_type": ["documentation", "tutorial", "guide", "readme"],
            "difficulty": [experience_level, "beginner"]
        }
        
       
        filter_by_purpose = self.agent_purposes.get("guide")
        
       
        boost_topic = learning_goal or "learning"
        
        return await self.retrieve(
            query=query,
            collection_types=collection_types,
            filters=filters,
            filter_by_purpose=filter_by_purpose,
            boost_topic=boost_topic,
            min_quality_score=0.6,  
            n_results=15,
            rerank=True,
            include_enriched_analysis=True
        )
    
    async def retrieve_for_mentor_agent(
        self,
        problem_description: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Enhanced contextual retrieval for troubleshooting and mentoring"""
        collection_types = ['main', 'code', 'documentation', 'slack_messages', 'tickets']
        
        
        detected_patterns = self._detect_problem_patterns(problem_description)
        
        
        enhanced_query = problem_description
        if detected_patterns:
            pattern_keywords = []
            for pattern in detected_patterns:
                pattern_keywords.extend(self.problem_patterns.get(pattern, [])[:2])
            enhanced_query += " " + " ".join(pattern_keywords[:3])
        
        
        filters = {}
        if context:
            if 'error_keywords' in context:
                filters["tags"] = context['error_keywords']
            if 'urgency' in context and context['urgency'] == 'high':
                filters["source_type"] = ["ticket", "issue", "troubleshooting", "solution"]
        
        
        if detected_patterns:
            troubleshooting_sources = ["documentation", "ticket", "issue", "solution", "troubleshooting"]
            if "source_type" in filters:
                filters["source_type"].extend(troubleshooting_sources)
            else:
                filters["source_type"] = troubleshooting_sources
        
        
        filter_by_purpose = self.agent_purposes.get("mentor")
        
        
        boost_topic = "troubleshooting"
        
        return await self.retrieve(
            query=enhanced_query,
            collection_types=collection_types,
            filters=filters if filters else None,
            filter_by_purpose=filter_by_purpose,
            boost_topic=boost_topic,
            min_quality_score=0.4, 
            n_results=12,
            rerank=True,
            include_enriched_analysis=True
        )
    
    async def retrieve_for_task_agent(
        self,
        user_id: str,
        user_role: str,
        skill_level: str,
        interests: List[str] = None
    ) -> Dict[str, Any]:
        """Enhanced retrieval with robust error handling"""
        try:
            query_parts = [user_role, skill_level]
            if interests:
                query_parts.extend(interests[:3])  # Limit interests
            
            query = " ".join(query_parts)
            
            # Use basic retrieval with error handling
            collections = ['tickets', 'pull_requests', 'main']
            
            try:
                results = await self.retrieve(
                    query=query,
                    collection_types=collections,
                    n_results=10
                )
                
                # FIX: Ensure consistent return format
                if not results:
                    return {"results": [], "query": query, "collections": collections}
                
                # FIX: Handle different result formats
                if isinstance(results, list):
                    return {"results": results, "query": query, "collections": collections}
                
                if isinstance(results, dict):
                    # Ensure results key exists
                    if "results" not in results:
                        results["results"] = []
                    return results
                
                # Fallback
                return {"results": [], "query": query, "collections": collections}
                
            except Exception as retrieval_error:
                logger.error(f"Retrieval error: {retrieval_error}")
                return {"results": [], "error": str(retrieval_error), "query": query}
                
        except Exception as e:
            logger.error(f"Task agent retrieval failed: {e}")
            return {"results": [], "error": str(e)}
            
    def _extract_primary_topic(self, query: str) -> str:
        """Extract primary topic from query for boosting"""
       
        common_topics = {
            "authentication": ["auth", "login", "token", "oauth"],
            "database": ["db", "database", "sql", "query"],
            "api": ["api", "endpoint", "request", "response"],
            "testing": ["test", "testing", "unit", "integration"],
            "deployment": ["deploy", "production", "docker", "kubernetes"],
            "frontend": ["react", "vue", "angular", "frontend", "ui"],
            "backend": ["server", "backend", "api", "service"]
        }
        
        query_lower = query.lower()
        for topic, keywords in common_topics.items():
            if any(keyword in query_lower for keyword in keywords):
                return topic
        
        return "general"
    
    def _detect_problem_patterns(self, problem_description: str) -> List[str]:
        """Detect known problem patterns in the description"""
        description_lower = problem_description.lower()
        detected = []
        
        for pattern_name, keywords in self.problem_patterns.items():
            if any(keyword in description_lower for keyword in keywords):
                detected.append(pattern_name)
        
        return detected
    
    def _infer_collection_types(self, query: str) -> List[str]:
        """Infer which collections to search based on query content"""
        query_lower = query.lower()
        collections = []
        
        if any(word in query_lower for word in ['function', 'class', 'method', 'variable', 'import', 'def']):
            collections.append('code')
        
        if any(word in query_lower for word in ['how to', 'tutorial', 'guide', 'documentation', 'readme']):
            collections.append('documentation')
        
        if any(word in query_lower for word in ['error', 'bug', 'issue', 'problem', 'fix']):
            collections.extend(['tickets', 'slack_messages'])
        
        if any(word in query_lower for word in ['change', 'update', 'modified', 'pull request', 'commit']):
            collections.append('pull_requests')
        
        if not collections:
            collections.append('main')
        
        return list(set(collections))
    
    def _build_context_filters(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build filters from user context"""
        filters = {}
        
        if 'current_repo' in context:
            filters['repository'] = context['current_repo']
        
        if 'team' in context:
            filters['team'] = context['team']
        
        if 'tech_stack' in context:
            filters['tags'] = context['tech_stack']
        
        if 'max_age_days' in context:
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=context['max_age_days'])
            filters['created_at'] = {'min': cutoff_date.isoformat()}
        
        return filters if filters else None



def quick_retrieve(
    query: str, 
    collection_types: List[str] = None, 
    user_id: str = None, 
    org_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Quick retrieval function with enhanced metadata support"""
    retriever = Retriever(user_id=user_id, org_id=org_id)
    import asyncio
    return asyncio.run(retriever.retrieve(query, collection_types, **kwargs))

def contextual_retrieve(
    query: str, 
    agent_type: str, 
    user_id: str = None, 
    org_id: str = None, 
    **kwargs
) -> Dict[str, Any]:
    """Contextual retrieval based on agent type with enriched metadata"""
    retriever = ContextualRetriever(user_id=user_id, org_id=org_id)
    import asyncio
    
    if agent_type == 'knowledge':
        return asyncio.run(retriever.retrieve_for_knowledge_agent(query, kwargs.get('context')))
    elif agent_type == 'guide':
        return asyncio.run(retriever.retrieve_for_guide_agent(
            kwargs.get('user_role', 'developer'),
            kwargs.get('learning_goal'),
            kwargs.get('experience_level', 'beginner')
        ))
    elif agent_type == 'mentor':
        return asyncio.run(retriever.retrieve_for_mentor_agent(query, kwargs.get('context')))
    elif agent_type == 'task':
        return asyncio.run(retriever.retrieve_for_task_agent(
            kwargs.get('user_role', 'developer'),
            kwargs.get('skill_level', 'beginner'),
            kwargs.get('interests')
        ))
    else:
        return asyncio.run(retriever.retrieve(query, **kwargs))

def enhanced_retrieve(
    query: str,
    user_id: str = None,
    org_id: str = None,
    filter_by_purpose: List[str] = None,
    min_quality_score: float = None,
    boost_topic: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Enhanced retrieval with full metadata integration"""
    retriever = Retriever(user_id=user_id, org_id=org_id)
    import asyncio
    return asyncio.run(retriever.retrieve(
        query=query,
        filter_by_purpose=filter_by_purpose,
        min_quality_score=min_quality_score,
        boost_topic=boost_topic,
        include_enriched_analysis=True,
        **kwargs
    ))

if __name__ == "__main__":
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            user_id = sys.argv[2] if len(sys.argv) > 2 else None
            org_id = sys.argv[3] if len(sys.argv) > 3 else None
            
            retriever = Retriever(user_id=user_id, org_id=org_id)
            
            if command == "test":
                query = sys.argv[4] if len(sys.argv) > 4 else "authentication system"
                result = await retriever.retrieve(query, include_enriched_analysis=True)
                print("Enhanced Retrieval Test Results:")
                print(json.dumps(result, indent=2))
                
            elif command == "enhanced":
                query = sys.argv[4] if len(sys.argv) > 4 else "API documentation"
                result = await retriever.retrieve(
                    query=query,
                    filter_by_purpose=["api_endpoint", "documentation"],
                    min_quality_score=0.6,
                    boost_topic="api",
                    include_enriched_analysis=True
                )
                print("Enhanced Retrieval with Metadata:")
                print(json.dumps(result, indent=2))
                
            elif command == "stats":
                stats = await retriever.get_retriever_stats()
                print("Enhanced Retriever Statistics:")
                print(json.dumps(stats, indent=2))
                
            elif command == "context":
                context = await retriever.get_user_context()
                print("User Context:")
                print(json.dumps(context, indent=2))
                
            elif command == "contextual":
                agent_type = sys.argv[4] if len(sys.argv) > 4 else "knowledge"
                query = sys.argv[5] if len(sys.argv) > 5 else "how to get started"
                
                contextual_retriever = ContextualRetriever(user_id=user_id, org_id=org_id)
                if agent_type == "knowledge":
                    result = await contextual_retriever.retrieve_for_knowledge_agent(query)
                elif agent_type == "guide":
                    result = await contextual_retriever.retrieve_for_guide_agent("developer", learning_goal=query)
                elif agent_type == "mentor":
                    result = await contextual_retriever.retrieve_for_mentor_agent(query)
                elif agent_type == "task":
                    result = await contextual_retriever.retrieve_for_task_agent("developer")
                else:
                    result = await retriever.retrieve(query)
                
                print(f"Enhanced Contextual Retrieval ({agent_type}):")
                print(json.dumps(result, indent=2))
                
            elif command == "quality":
                
                query = sys.argv[4] if len(sys.argv) > 4 else "database connection"
                min_quality = float(sys.argv[5]) if len(sys.argv) > 5 else 0.7
                
                result = await retriever.retrieve(
                    query=query,
                    min_quality_score=min_quality,
                    include_enriched_analysis=True
                )
                print(f"Quality-Filtered Retrieval (min_quality: {min_quality}):")
                print(json.dumps(result, indent=2))
                
            elif command == "purpose":
               
                query = sys.argv[4] if len(sys.argv) > 4 else "testing framework"
                purposes = sys.argv[5].split(',') if len(sys.argv) > 5 else ["testing", "documentation"]
                
                result = await retriever.retrieve(
                    query=query,
                    filter_by_purpose=purposes,
                    include_enriched_analysis=True
                )
                print(f"Purpose-Filtered Retrieval (purposes: {purposes}):")
                print(json.dumps(result, indent=2))
                
            else:
                print("Available commands:")
                print("  test [query] - Test basic enhanced retrieval")
                print("  enhanced [query] - Test enhanced retrieval with metadata")
                print("  stats - Show enhanced retriever statistics")
                print("  context - Show user context")
                print("  contextual [agent_type] [query] - Test contextual retrieval")
                print("  quality [query] [min_score] - Test quality-based filtering")
                print("  purpose [query] [purposes] - Test purpose-based filtering")
        else:
            print("Usage: python retriever.py [command] [user_id] [org_id] [args...]")
            print("Enhanced retriever with enriched metadata integration")
    
    asyncio.run(main())