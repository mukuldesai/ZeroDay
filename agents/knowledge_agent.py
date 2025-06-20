import os
import yaml
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions
import openai
from anthropic import Anthropic
from functools import lru_cache

class KnowledgeAgent:
    """
    Knowledge Agent: Searches codebase, docs, PRs, and team context
    to answer technical questions with relevant context
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.chroma_client = None
        self.collection = None
        self.llm_client = None
        self._initialize_components()
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_components(self):
        """Initialize ChromaDB and LLM clients"""
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=os.path.join(os.path.dirname(__file__), "..", "vector_store", "chroma_db")
            )
            
            embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=self.config['vector_store']['embedding_model']
            )
            
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.config['vector_store']['collection_name'],
                    embedding_function=embedding_function
                )
                logger.info("Connected to existing ChromaDB collection")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=self.config['vector_store']['collection_name'],
                    embedding_function=embedding_function
                )
                logger.info("Created new ChromaDB collection")
            
            if self.config['llm']['provider'] == 'openai':
                self.llm_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            elif self.config['llm']['provider'] == 'anthropic':
                self.llm_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            logger.info(f"Knowledge Agent initialized with {self.config['llm']['provider']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Agent: {str(e)}")
            raise
    
    async def query(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main query method - searches knowledge base and generates response
        """
        try:
            logger.info(f"Processing knowledge query: {question[:100]}...")
            search_results = self._search_knowledge_base(question)
            response = await self._generate_response(question, search_results, context)
            return {
                "response": response,
                "confidence": self._calculate_confidence(search_results),
                "sources": self._format_sources(search_results),
                "suggestions": self._generate_suggestions(question, search_results),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in knowledge query: {str(e)}")
            return {
                "response": f"I encountered an error while searching the knowledge base: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "suggestions": ["Try rephrasing your question", "Check if the knowledge base is populated"],
                "timestamp": datetime.now().isoformat()
            }

    @lru_cache(maxsize=100)
    def _search_knowledge_base(self, query: str, n_results: int = None) -> List[Dict]:
        """Search ChromaDB for relevant documents"""
        if not n_results:
            n_results = self.config['agents']['knowledge']['max_results']
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'][0] else 1.0
                    })
            
            logger.info(f"Found {len(formatted_results)} relevant documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    async def _generate_response(self, question: str, search_results: List[Dict], context: Dict = None) -> str:
        """Generate response using LLM with retrieved context"""
        
        context_text = self._build_context_text(search_results)
        
        prompt_template = self._load_prompt_template("general_query.txt")
        
        formatted_prompt = prompt_template.format(
            question=question,
            context=context_text,
            user_context = context.get("chat_history", "No additional context provided") if context else "No additional context provided"
        )
        
        logger.debug(f"Formatted prompt:\n{formatted_prompt}")

        try:
            if self.config['llm']['provider'] == 'openai':
                response = self.llm_client.chat.completions.create(
                    model=self.config['llm']['model'],
                    messages=[
                        {"role": "system", "content": "You are a helpful knowledge agent that answers technical questions using provided context."},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    temperature=self.config['llm']['temperature'],
                    max_tokens=self.config['llm']['max_tokens']
                )
                return response.choices[0].message.content
                
            elif self.config['llm']['provider'] == 'anthropic':
                response = self.llm_client.messages.create(
                    model=self.config['llm']['model'],
                    max_tokens=self.config['llm']['max_tokens'],
                    temperature=self.config['llm']['temperature'],
                    messages=[
                        {"role": "user", "content": formatted_prompt}
                    ]
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return f"I found relevant information but encountered an error generating the response: {str(e)}"
    
    def _build_context_text(self, search_results: List[Dict]) -> str:
        """Build context text from search results"""
        if not search_results:
            return "No relevant context found in the knowledge base."
        
        context_parts = []
        for i, result in enumerate(search_results[:5]):  
            metadata = result.get('metadata', {})
            source_info = f"Source: {metadata.get('source_type', 'unknown')} - {metadata.get('file_path', 'unknown')}"
            
            context_parts.append(f"Context {i+1} ({source_info}):\n{result['content']}\n")
        
        return "\n".join(context_parts)
    
    def _load_prompt_template(self, template_name: str) -> str:
        """Load prompt template from configs/prompts/"""
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "configs", "prompts", template_name
        )
        
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt template {template_name} not found, using default")
            return """
            Question: {question}
            
            Context from knowledge base:
            {context}
            
            Additional context: {user_context}
            
            Please provide a helpful and accurate answer based on the provided context. If the context doesn't contain enough information, say so clearly.
            """
    
    def _calculate_confidence(self, search_results: List[Dict]) -> float:
        """Calculate confidence score based on search results quality"""
        if not search_results:
            return 0.0

        distances = [result.get('distance', 1.0) for result in search_results]
        avg_distance = sum(distances) / len(distances)
        
        confidence = max(0.0, 1.0 - avg_distance)
        return round(confidence, 2)
    
    def _format_sources(self, search_results: List[Dict]) -> List[Dict[str, str]]:
        """Format search results into source references"""
        sources = []
        for result in search_results[:3]:  
            metadata = result.get('metadata', {})
            sources.append({
                "type": metadata.get('source_type', 'unknown'),
                "path": metadata.get('file_path', 'unknown'),
                "section": metadata.get('section', ''),
                "lines": metadata.get('lines', '')
            })
        return sources
    
    def _generate_suggestions(self, question: str, search_results: List[Dict]) -> List[str]:
        """Generate helpful suggestions based on query and results"""
        suggestions = []
        
        if not search_results:
            suggestions.extend([
                "Try using different keywords",
                "Check if the knowledge base has been populated",
                "Ask a more specific question"
            ])
        else:

            topics = set()
            for result in search_results:
                metadata = result.get('metadata', {})
                if 'tags' in metadata:
                    topics.update(metadata['tags'])
            
            if topics:
                suggestions.append(f"Related topics: {', '.join(list(topics)[:3])}")
            
            suggestions.extend([
                "Check the related source files for more details",
                "Ask about specific implementation details",
                "Look for related PRs or documentation"
            ])
        
        return suggestions
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.config['vector_store']['collection_name'],
                "embedding_model": self.config['vector_store']['embedding_model'],
                "status": "healthy" if count > 0 else "empty"
            }
        except Exception as e:
            return {
                "total_documents": 0,
                "collection_name": self.config['vector_store']['collection_name'],
                "status": f"error: {str(e)}"
            }