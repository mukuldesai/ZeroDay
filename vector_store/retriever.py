import os
import yaml
from typing import List, Dict, Any, Optional, Union
from loguru import logger
from datetime import datetime
import numpy as np
from chromadb_setup import ChromaDBSetup

class Retriever:
    """
    Advanced Retriever: Intelligent context retrieval for all agents
    Supports multi-collection search, re-ranking, and contextual filtering
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.db_setup = ChromaDBSetup(config_path)
        self.db_setup.initialize_client()
        self.collections = self.db_setup.setup_collections()
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def retrieve(
        self,
        query: str,
        collection_types: List[str] = None,
        n_results: int = None,
        filters: Dict[str, Any] = None,
        rerank: bool = True,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Main retrieval method with advanced filtering and ranking
        
        Args:
            query: Search query string
            collection_types: Which collections to search (['main', 'code', 'docs'])
            n_results: Number of results to return (default from config)
            filters: Metadata filters to apply
            rerank: Whether to apply re-ranking algorithms
            include_metadata: Whether to include full metadata in results
        """
        try:
            if not n_results:
                n_results = self.config['agents']['knowledge']['max_results']
            
            if not collection_types:
                collection_types = ['main'] 
            
            logger.info(f"Retrieving from collections: {collection_types}")
            
            all_results = []
            for collection_type in collection_types:
                if collection_type in self.collections:
                    results = await self._search_collection(
                        query=query,
                        collection=self.collections[collection_type],
                        collection_type=collection_type,
                        n_results=n_results,
                        filters=filters
                    )
                    all_results.extend(results)
       
            if rerank and all_results:
                all_results = self._rerank_results(query, all_results)
            
            final_results = all_results[:n_results]
            relevance_stats = self._calculate_relevance_stats(final_results)
            
            return {
                "results": final_results,
                "query": query,
                "collections_searched": collection_types,
                "total_results": len(final_results),
                "relevance_stats": relevance_stats,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in retrieval: {str(e)}")
            return {
                "results": [],
                "query": query,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _search_collection(
        self,
        query: str,
        collection,
        collection_type: str,
        n_results: int,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search a single collection with filters"""
        try:
            where_clause = self._build_where_clause(filters) if filters else None
        
            results = collection.query(
                query_texts=[query],
                n_results=n_results * 2, 
                where=where_clause,
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'][0] else 1.0,
                        'collection_type': collection_type,
                        'relevance_score': 1.0 - results['distances'][0][i] if results['distances'][0] else 0.0
                    }
                    
                    result['metadata']['collection_type'] = collection_type
                    
                    formatted_results.append(result)
            
            logger.debug(f"Found {len(formatted_results)} results in {collection_type}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching collection {collection_type}: {str(e)}")
            return []
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build ChromaDB where clause from filters"""
        where_clause = {}
        
        for key, value in filters.items():
            if isinstance(value, list):
                where_clause[key] = {"$in": value}
            elif isinstance(value, dict):
                if 'min' in value or 'max' in value:
                    range_filter = {}
                    if 'min' in value:
                        range_filter["$gte"] = value['min']
                    if 'max' in value:
                        range_filter["$lte"] = value['max']
                    where_clause[key] = range_filter
            else:
                where_clause[key] = {"$eq": value}
        
        return where_clause
    
    def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-rank results using multiple signals"""
        try:
            deduplicated = self._deduplicate_results(results)
            
            for result in deduplicated:
                result['final_score'] = self._calculate_final_score(query, result)
            
            ranked_results = sorted(deduplicated, key=lambda x: x['final_score'], reverse=True)
            
            logger.debug(f"Re-ranked {len(results)} -> {len(ranked_results)} results")
            return ranked_results
            
        except Exception as e:
            logger.error(f"Error re-ranking results: {str(e)}")
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
        """Calculate final ranking score using multiple signals"""
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
    
    def _calculate_relevance_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics about result relevance"""
        if not results:
            return {"avg_score": 0.0, "min_score": 0.0, "max_score": 0.0, "score_distribution": {}}
        
        scores = [r.get('final_score', r.get('relevance_score', 0.0)) for r in results]
        
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
        filters = {"file_path": source_path}
        
        return await self.retrieve(
            query="",  
            collection_types=collection_types,
            n_results=n_results,
            filters=filters,
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
    
    async def get_retriever_stats(self) -> Dict[str, Any]:
        """Get comprehensive retriever statistics"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "collections": {},
            "config": {
                "distance_threshold": self.config['vector_store']['distance_threshold'],
                "max_results": self.config['agents']['knowledge']['max_results']
            }
        }
        
        try:
            for collection_name, collection in self.collections.items():
                count = collection.count()
                
                if count > 0:
                    sample = collection.get(limit=5, include=['metadatas'])
                    
                    source_types = set()
                    file_extensions = set()
                    
                    for metadata in sample.get('metadatas', []):
                        if metadata:
                            source_types.add(metadata.get('source_type', 'unknown'))
                            file_path = metadata.get('file_path', '')
                            if '.' in file_path:
                                file_extensions.add(file_path.split('.')[-1])
                    
                    stats["collections"][collection_name] = {
                        "document_count": count,
                        "source_types": list(source_types),
                        "file_extensions": list(file_extensions)
                    }
                else:
                    stats["collections"][collection_name] = {
                        "document_count": 0,
                        "source_types": [],
                        "file_extensions": []
                    }
        
        except Exception as e:
            stats["error"] = str(e)
        
        return stats


class ContextualRetriever(Retriever):
    """
    Enhanced retriever with contextual understanding for different agent types
    """
    
    def __init__(self, config_path: str = None):
        super().__init__(config_path)
        self.problem_patterns = {
            "authentication_error": ["auth", "login", "token", "unauthorized", "403", "401"],
            "database_connection": ["database", "db", "connection", "timeout", "pool"],
            "build_failure": ["build", "compile", "webpack", "npm", "yarn", "error"],
            "deployment_issue": ["deploy", "production", "server", "docker", "k8s"],
            "performance_problem": ["slow", "performance", "memory", "cpu", "optimization"]
        }
    
    async def retrieve_for_knowledge_agent(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimized retrieval for knowledge agent queries"""
        collection_types = self._infer_collection_types(query)
        filters = self._build_context_filters(context) if context else None
        
        return await self.retrieve(
            query=query,
            collection_types=collection_types,
            filters=filters,
            n_results=self.config['agents']['knowledge']['max_results'],
            rerank=True
        )
    
    async def retrieve_for_guide_agent(
        self,
        user_role: str,
        learning_goal: str = None,
        experience_level: str = "beginner"
    ) -> Dict[str, Any]:
        """Specialized retrieval for learning path generation"""
        collection_types = ['documentation', 'main']
        
        query_parts = [user_role]
        if learning_goal:
            query_parts.append(learning_goal)
        
        query = " ".join(query_parts)
        
        filters = {
            "source_type": ["documentation", "tutorial", "guide", "readme"],
            "difficulty": [experience_level, "beginner"]  
        }
        
        return await self.retrieve(
            query=query,
            collection_types=collection_types,
            filters=filters,
            n_results=15,
            rerank=True
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
        
        return await self.retrieve(
            query=enhanced_query,
            collection_types=collection_types,
            filters=filters if filters else None,
            n_results=12,
            rerank=True
        )
    
    async def retrieve_for_task_agent(
        self,
        user_role: str,
        skill_level: str = "beginner",
        interests: List[str] = None
    ) -> Dict[str, Any]:
        """Retrieve suitable tasks and assignments"""
        collection_types = ['tickets', 'pull_requests', 'main']
        
        query = f"{user_role} {skill_level} tasks"
        if interests:
            query += " " + " ".join(interests)
        
        filters = {
            "source_type": ["ticket", "issue", "task", "bug"],
            "difficulty": [skill_level, "beginner"],
            "status": ["open", "todo", "unassigned"]
        }
        
        return await self.retrieve(
            query=query,
            collection_types=collection_types,
            filters=filters,
            n_results=10,
            rerank=True
        )
    
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


def quick_retrieve(query: str, collection_types: List[str] = None) -> Dict[str, Any]:
    """Quick retrieval function for simple use cases"""
    retriever = Retriever()
    import asyncio
    return asyncio.run(retriever.retrieve(query, collection_types))

def contextual_retrieve(query: str, agent_type: str, **kwargs) -> Dict[str, Any]:
    """Contextual retrieval based on agent type"""
    retriever = ContextualRetriever()
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
        return asyncio.run(retriever.retrieve(query))

if __name__ == "__main__":
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            retriever = Retriever()
            
            if command == "test":
                query = sys.argv[2] if len(sys.argv) > 2 else "authentication system"
                result = await retriever.retrieve(query)
                print("Retrieval Test Results:")
                print(json.dumps(result, indent=2))
                
            elif command == "stats":
                stats = await retriever.get_retriever_stats()
                print("Retriever Statistics:")
                print(json.dumps(stats, indent=2))
                
            elif command == "contextual":
                agent_type = sys.argv[2] if len(sys.argv) > 2 else "knowledge"
                query = sys.argv[3] if len(sys.argv) > 3 else "how to get started"
                
                contextual_retriever = ContextualRetriever()
                if agent_type == "knowledge":
                    result = await contextual_retriever.retrieve_for_knowledge_agent(query)
                elif agent_type == "guide":
                    result = await contextual_retriever.retrieve_for_guide_agent("developer", query)
                elif agent_type == "mentor":
                    result = await contextual_retriever.retrieve_for_mentor_agent(query)
                elif agent_type == "task":
                    result = await contextual_retriever.retrieve_for_task_agent("developer")
                else:
                    result = await retriever.retrieve(query)
                
                print(f"Contextual Retrieval ({agent_type}):")
                print(json.dumps(result, indent=2))
                
            else:
                print("Available commands:")
                print("  test [query] - Test basic retrieval")
                print("  stats - Show retriever statistics")
                print("  contextual [agent_type] [query] - Test contextual retrieval")
        else:
            print("Usage: python retriever.py [test|stats|contextual] [args...]")
    
    asyncio.run(main())