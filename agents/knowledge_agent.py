import os
import sys
import yaml
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime, timedelta
import openai
from anthropic import Anthropic
from dotenv import load_dotenv

import chromadb
chromadb.telemetry.capture = lambda *args, **kwargs: None

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vector_store.chromadb_setup import ChromaDBSetup

class KnowledgeAgent:
    def __init__(self, config_path: str = None, demo_mode: bool = True):
        """Initialize Knowledge Agent with document-aware capabilities"""
        self.config = self._load_config(config_path)
        self.demo_mode = demo_mode
        self.user_id = "demo_user" if demo_mode else "current_user"
        self.org_id = "demo_org" if demo_mode else "default_org"
        
        
        self.llm_client = None
        self.llm_provider = None
        self.llm_initialized = False
        
        try:
            self._initialize_llm()
        except Exception as e:
            logger.error(f"LLM initialization failed during constructor: {e}")
            
       
        try:
            self.db_setup = ChromaDBSetup(config_path, self.user_id, self.org_id)
            self.db_setup.initialize_client()
            self.collections = self.db_setup.setup_collections()
            logger.info("ChromaDB setup completed successfully")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            self.collections = {}
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration with error handling"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from: {config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            
            return {
                'llm': {'provider': 'openai', 'model': 'gpt-3.5-turbo'},
                'vector_store': {'collection_name': 'default', 'embedding_model': 'default'}
            }
    
    def _initialize_llm(self):
        """Initialize LLM client with comprehensive error handling and debugging"""
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            
            print(f"🔑 OpenAI key present: {'Yes' if openai_key else 'No'}")
            print(f"🔑 Anthropic key present: {'Yes' if anthropic_key else 'No'}")
            print(f"🔑 Provider configured: {self.config['llm']['provider']}")
            
            if self.config['llm']['provider'] == 'openai':
                if not openai_key:
                    raise ValueError("OpenAI API key not found in environment variables!")
                
                self.llm_client = openai.OpenAI(api_key=openai_key)
                self.llm_provider = 'openai'
                print(" OpenAI client initialized successfully")
                
            elif self.config['llm']['provider'] == 'anthropic':
                if not anthropic_key:
                    raise ValueError("Anthropic API key not found in environment variables!")
                
                self.llm_client = Anthropic(api_key=anthropic_key)
                self.llm_provider = 'anthropic'
                print(" Anthropic client initialized successfully")
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.config['llm']['provider']}")
            
            if self.llm_client is None:
                raise RuntimeError("LLM client is None after initialization")
            
            self.llm_initialized = True
            logger.info(f"Knowledge Agent LLM initialized with {self.config['llm']['provider']}")
            
        except Exception as e:
            self.llm_client = None
            self.llm_provider = None
            self.llm_initialized = False
            error_msg = f"Failed to initialize LLM: {str(e)}"
            print(f" {error_msg}")
            logger.error(error_msg)
            raise  
    
    def _call_llm_with_fallback(self, messages, **kwargs):
        """Call LLM with automatic fallback"""
        
        # Try primary provider first
        if self.llm_client and self.llm_provider:
            try:
                return self._make_llm_call(self.llm_client, self.llm_provider, messages, **kwargs)
            except Exception as e:
                logger.warning(f"Knowledge Agent - Primary LLM ({self.llm_provider}) failed: {e}")
                
                
                raise
        else:
            raise RuntimeError("No LLM client available")

    def _make_llm_call(self, client, provider, messages, **kwargs):
        """Make actual LLM API call"""
        if provider == 'openai':
            response = client.chat.completions.create(
                model=self.config['llm']['model'],
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1000),
                timeout=30
            )
            return response.choices[0].message.content.strip()
            
        elif provider == 'anthropic':
            
            if isinstance(messages, list) and len(messages) > 1:
                system_msg = messages[0]['content'] if messages[0]['role'] == 'system' else ''
                user_msg = messages[1]['content'] if len(messages) > 1 else messages[0]['content']
                combined_prompt = f"{system_msg}\n\n{user_msg}"
            else:
                combined_prompt = messages[0]['content'] if isinstance(messages, list) else str(messages)
                
            response = client.messages.create(
                model=self.config['llm'].get('fallback_model', 'claude-3-haiku-20240307'),
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                messages=[{"role": "user", "content": combined_prompt}]
            )
            return response.content[0].text.strip()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _check_llm_availability(self) -> bool:
        """Check if LLM is available for use"""
        if not self.llm_initialized or self.llm_client is None:
            logger.warning("LLM client not available - using fallback responses")
            return False
        return True
    
    def _clean_text_fast(self, text: str) -> str:
        """Fast text cleaning - simplified version"""
        if not text:
            return ""
        
        try:
            text = str(text)[:3000]
            text = text.replace('\x8f', '').replace('\x9f', '').replace('\x81', '').replace('\x9d', '')
            cleaned = ''.join(c for c in text if 32 <= ord(c) <= 126 or c in '\n\r\t')
            return cleaned[:2500]
        except Exception:
            return "Content processing error"
    
    def _clean_dict_fast(self, data: dict) -> dict:
        """Fast dictionary cleaning"""
        if not isinstance(data, dict):
            return {}
        
        cleaned = {}
        for key, value in list(data.items())[:10]:
            try:
                if isinstance(value, str):
                    cleaned[str(key)] = self._clean_text_fast(value)
                elif isinstance(value, (int, float, bool)):
                    cleaned[str(key)] = value
                else:
                    cleaned[str(key)] = str(value)[:200]
            except:
                cleaned[str(key)] = "error"
        
        return cleaned

    def _analyze_question_context(self, question: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced context analysis for better responses"""
        question_lower = question.lower()
        context = user_context.copy() if user_context else {}
        
        
        if any(word in question_lower for word in ["how", "setup", "configure", "install"]):
            context["intent"] = "how_to"
        elif any(word in question_lower for word in ["what", "explain", "understand"]):
            context["intent"] = "explanation"
        elif any(word in question_lower for word in ["error", "broken", "issue", "problem"]):
            context["intent"] = "troubleshooting"
        elif any(word in question_lower for word in ["best", "recommend", "should"]):
            context["intent"] = "guidance"
        elif any(word in question_lower for word in ["document", "file", "uploaded", "my"]):
            context["intent"] = "document_specific"
        else:
            context["intent"] = "general"
        
        
        tech_keywords = {
            "react": ["react", "jsx", "hooks", "component"],
            "authentication": ["auth", "login", "token", "jwt", "session"],
            "database": ["database", "sql", "query", "db", "mongo", "postgres"],
            "api": ["api", "endpoint", "rest", "graphql", "request"],
            "deployment": ["deploy", "production", "server", "hosting"],
            "testing": ["test", "unit", "integration", "cypress"],
            "documents": ["document", "file", "pdf", "upload", "content"]
        }
        
        context["topics"] = []
        for topic, keywords in tech_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                context["topics"].append(topic)
        
      
        if any(word in question_lower for word in ["urgent", "quickly", "asap", "broken"]):
            context["urgency"] = "high"
        elif any(word in question_lower for word in ["learn", "understand", "guide"]):
            context["urgency"] = "low"
        else:
            context["urgency"] = "medium"
        
       
        context["document_focused"] = any(word in question_lower for word in [
            "my document", "uploaded file", "my file", "in the document", 
            "according to", "from the file", "document says"
        ])
        
        return context

    async def query(self, question: str, user_id: str = "default", user_context: Dict[str, Any] = None, demo_mode: bool = True) -> Dict[str, Any]:
        """Enhanced query method with document-aware capabilities"""
        try:
            
            question = self._clean_text_fast(question)
            user_id = self._clean_text_fast(user_id or "current_user")
            user_context = self._clean_dict_fast(user_context or {})

            if not question.strip():
                return self._create_helpful_response(
                    "I'm here to help with any questions about our codebase, documentation, or your uploaded documents. What would you like to know?",
                    user_id
                )

            logger.info(f" Processing knowledge query for user {user_id}: {question[:100]}... (demo_mode: {demo_mode})")

            
            enriched_context = self._analyze_question_context(question, user_context)

            
            try:
                document_results = await self._search_user_documents(question, user_id, enriched_context, demo_mode)
                general_results = await self._search_knowledge_base_enhanced(question, enriched_context, demo_mode)
                
               
                all_results = self._combine_and_prioritize_results(document_results, general_results, enriched_context)
                context_text = self._format_context_for_llm_with_citations(all_results)
                
            except Exception as e:
                logger.warning(f"Context retrieval failed: {e}")
                all_results = []
                context_text = "ZeroDay AI platform with React frontend, FastAPI backend, and specialized AI agents"

           
            if not self._check_llm_availability():
                print("  LLM not available - using contextual fallback response")
                response = self._create_contextual_fallback_with_documents(question, enriched_context, all_results)
            else:
                try:
                    print(f" Attempting LLM call for: {question[:50]}...")
                    response = await self._generate_enhanced_response_with_citations(question, context_text, enriched_context, all_results)
                    print(f" LLM response received: {len(response)} characters")
                except Exception as e:
                    print(f" LLM call failed: {e}")
                    logger.error(f"LLM call failed: {e}")
                    response = self._create_contextual_fallback_with_documents(question, enriched_context, all_results)

           
            citations = self._extract_citations(all_results)

            return {
                "success": True,
                "response": response,
                "confidence": 0.95 if document_results and self.llm_initialized else 0.9 if all_results and self.llm_initialized else 0.7,
                "agent_type": "knowledge",
                "sources": all_results[:5],
                "citations": citations,
                "document_sources": [r for r in all_results if r.get('is_user_document', False)],
                "enriched_context": enriched_context,
                "suggestions": self._generate_suggestions_enhanced(question, enriched_context),
                "user_id": user_id,
                "llm_available": self.llm_initialized,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            logger.error(f"Knowledge query failed: {e}")
            return {
                "success": False,
                "response": "I encountered an issue processing your question. Could you try rephrasing it or asking about a specific aspect?",
                "confidence": 0.3,
                "agent_type": "knowledge",
                "user_id": user_id,
                "llm_available": self.llm_initialized,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    async def _search_user_documents(self, query: str, user_id: str, context: Dict[str, Any], demo_mode: bool) -> List[Dict]:
        """ Search specifically in user's uploaded documents"""
        try:
            
            collection = self.collections.get("main") or self.collections.get("code")
            
            if not collection:
                logger.warning("No collection available for user document search")
                return []
           
            results = collection.query(
                query_texts=[query],
                n_results=10,
                include=['documents', 'metadatas', 'distances'],
                where={"user_id": user_id}  # 🔍 Filter by user ID
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    content = self._clean_text_fast(results['documents'][0][i])
                    metadata = self._clean_dict_fast(results['metadatas'][0][i] if results['metadatas'][0] else {})
                    distance = results['distances'][0][i] if results['distances'][0] else 0.5
                    
                   
                    upload_time = metadata.get('upload_time', '')
                    recency_boost = self._calculate_recency_boost(upload_time)
                    
                    result_data = {
                        'content': content[:800],
                        'metadata': metadata,
                        'relevance_score': max(0.0, 1.0 - distance) + recency_boost,
                        'is_user_document': True,
                        'source_file': metadata.get('source_file', 'Unknown Document'),
                        'document_id': metadata.get('document_id', ''),
                        'upload_time': upload_time
                    }
                    formatted_results.append(result_data)
            
            
            formatted_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            logger.info(f"📄 Found {len(formatted_results)} user documents for query")
            return formatted_results[:5]
            
        except Exception as e:
            logger.error(f"Error searching user documents: {str(e)}")
            return []

    def _calculate_recency_boost(self, upload_time: str) -> float:
        """Calculate boost for recently uploaded documents"""
        try:
            if not upload_time:
                return 0.0
            
            upload_dt = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
            now = datetime.now()
            hours_ago = (now - upload_dt.replace(tzinfo=None)).total_seconds() / 3600
            
           
            if hours_ago < 1:
                return 0.3 
            elif hours_ago < 6:
                return 0.2  
            elif hours_ago < 24:
                return 0.1  
            else:
                return 0.0 
                
        except Exception:
            return 0.0

    async def _search_knowledge_base_enhanced(self, query: str, context: Dict[str, Any], demo_mode: bool) -> List[Dict]:
        """Enhanced knowledge base search for general platform knowledge"""
        try:
            query_topics = context.get('topics', [])
            if 'authentication' in query_topics:
                collection = self.collections.get("code") or self.collections.get("main")
            elif 'database' in query_topics:
                collection = self.collections.get("code") or self.collections.get("main")
            elif context.get('intent') == 'how_to':
                collection = self.collections.get("documentation") or self.collections.get("main")
            else:
                collection = self.collections.get("main") or self.collections.get("code")
            
            if not collection:
                logger.error(f"No collection available for query: {query}")
                return []
           
            results = collection.query(
                query_texts=[query],
                n_results=5,
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    content = self._clean_text_fast(results['documents'][0][i])
                    metadata = self._clean_dict_fast(results['metadatas'][0][i] if results['metadatas'][0] else {})
                    distance = results['distances'][0][i] if results['distances'][0] else 0.5
                    
                    result_data = {
                        'content': content[:800],
                        'metadata': metadata,
                        'relevance_score': max(0.0, 1.0 - distance),
                        'is_user_document': False,
                        'source_file': metadata.get('source_type', 'Platform Knowledge'),
                        'document_id': '',
                        'upload_time': ''
                    }
                    formatted_results.append(result_data)
            
            formatted_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            logger.info(f"🔍 Found {len(formatted_results)} general knowledge documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in enhanced knowledge base search: {str(e)}")
            return []

    def _combine_and_prioritize_results(self, document_results: List[Dict], general_results: List[Dict], context: Dict[str, Any]) -> List[Dict]:
        """Combine and prioritize user documents vs general knowledge"""
        
        
        if context.get('document_focused', False) or context.get('intent') == 'document_specific':
       
            combined = document_results + general_results
        else:
            
            for doc in document_results:
                doc['relevance_score'] += 0.1  
            
            combined = document_results + general_results
            combined.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return combined[:8]  

    def _format_context_for_llm_with_citations(self, results: List[Dict]) -> str:
        """Format search results for LLM with proper citation markers"""
        if not results:
            return "ZeroDay AI platform - React frontend, FastAPI backend with Python, specialized AI agents"
        
        context_parts = []
        for i, result in enumerate(results[:5]):
            content = result['content'][:400]
            source_file = result.get('source_file', 'Unknown')
            is_user_doc = result.get('is_user_document', False)
            upload_time = result.get('upload_time', '')
            
            if is_user_doc:
                source_label = f" User Document: {source_file}"
                if upload_time:
                    try:
                        upload_dt = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
                        time_str = upload_dt.strftime("%Y-%m-%d %H:%M")
                        source_label += f" (uploaded {time_str})"
                    except:
                        pass
            else:
                source_label = f" Platform Knowledge: {source_file}"
            
            context_parts.append(f"[Source {i+1}] {source_label}:\n{content}")
        
        return "\n\n".join(context_parts)

    async def _generate_enhanced_response_with_citations(self, question: str, context: str, enriched_context: Dict[str, Any], results: List[Dict]) -> str:
        """Generate enhanced response with proper citations"""
        if not self._check_llm_availability():
            raise RuntimeError("LLM client not available")
        
        intent = enriched_context.get('intent', 'general')
        topics = ', '.join(enriched_context.get('topics', ['general']))
        urgency = enriched_context.get('urgency', 'medium')
        has_user_docs = any(r.get('is_user_document', False) for r in results)
        
        system_prompt = self._load_enhanced_prompt_template_with_citations()
        
        user_prompt = f"""Question: {question}

Context from ZeroDay platform and user documents:
{context}

Question Intent: {intent}
Technical Topics: {topics}
Urgency Level: {urgency}
User Documents Available: {has_user_docs}

IMPORTANT: When referencing information from sources, use citations like:
- For user documents: "According to your document 'filename.pdf'..." or "As mentioned in your uploaded file 'report.docx'..."
- For platform knowledge: "Based on the ZeroDay platform..." or "According to our codebase..."

Provide a helpful, specific response that directly addresses the question. Include relevant examples and clear citations when referencing sources."""

        try:
            if self.llm_provider == 'openai':
                response = self.llm_client.chat.completions.create(
                    model=self.config['llm']['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=30
                )
                return response.choices[0].message.content.strip()
                
            elif self.llm_provider == 'anthropic':
                response = self.llm_client.messages.create(
                    model=self.config['llm']['model'],
                    max_tokens=1000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}]
                )
                return response.content[0].text.strip()
                
            else:
                raise ValueError(f"Unsupported provider: {self.llm_provider}")
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    def _load_enhanced_prompt_template_with_citations(self) -> str:
        """Load enhanced prompt template with citation instructions"""
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "configs", "prompts", "general_query.txt"
        )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt template not found, using default")
            return """You are Alex Thompson, a senior developer who knows the ZeroDay AI platform inside and out. You provide clear, helpful answers about the codebase, architecture, and development practices.

The ZeroDay platform includes:
- React/TypeScript frontend with modern patterns
- FastAPI backend with Python
- ChromaDB vector database
- 4 specialized AI agents (Knowledge, Task, Mentor, Guide)
- Authentication system with JWT
- File upload and processing capabilities

CITATION REQUIREMENTS:
- When referencing user documents, always cite them: "According to your document 'filename.pdf'..."
- When referencing platform knowledge, mention: "Based on the ZeroDay platform..." 
- Be specific about which document or source contains the information
- Use natural language for citations, not formal academic style

Provide specific, actionable answers. Reference code examples when relevant. Be conversational but technical."""

    def _extract_citations(self, results: List[Dict]) -> List[Dict]:
        """Extract citation information from search results"""
        citations = []
        for result in results[:5]:
            if result.get('is_user_document', False):
                citations.append({
                    'type': 'user_document',
                    'source_file': result.get('source_file', 'Unknown Document'),
                    'document_id': result.get('document_id', ''),
                    'upload_time': result.get('upload_time', ''),
                    'relevance_score': result.get('relevance_score', 0.0)
                })
            else:
                citations.append({
                    'type': 'platform_knowledge',
                    'source_file': result.get('source_file', 'Platform Knowledge'),
                    'metadata': result.get('metadata', {}),
                    'relevance_score': result.get('relevance_score', 0.0)
                })
        
        return citations

    def _create_contextual_fallback_with_documents(self, question: str, context: Dict[str, Any], search_results: List[Dict]) -> str:
        """Create contextual fallback response that includes document awareness"""
        intent = context.get('intent', 'general')
        topics = context.get('topics', [])
        has_user_docs = any(r.get('is_user_document', False) for r in search_results)
        
       
        user_docs = [r.get('source_file', 'Unknown') for r in search_results if r.get('is_user_document', False)]
        
        base_response = ""
        
        if intent == 'troubleshooting':
            base_response = f"""I understand you're experiencing an issue. Based on our ZeroDay codebase{' and your uploaded documents' if has_user_docs else ''}, here are some general troubleshooting steps:

1. Check the console for specific error messages
2. Verify your environment configuration
3. Review recent changes in the relevant files
4. Check our troubleshooting documentation

{f"Since this involves {', '.join(topics)}, you might want to check the related configuration files and documentation." if topics else ""}"""
        
        elif intent == 'how_to':
            base_response = f"""I'd be happy to help you with setup and configuration. For the ZeroDay platform{' and based on your documents' if has_user_docs else ''}:

1. Check our setup documentation for step-by-step guides
2. Review the relevant configuration files
3. Look at existing examples in the codebase
4. Verify your development environment

{f"For {', '.join(topics)}-related setup, there are specific guides in our documentation." if topics else ""}"""
        
        elif intent == 'explanation':
            base_response = f"""Based on the ZeroDay platform architecture{' and your uploaded documents' if has_user_docs else ''}, I can help explain how our system works:

- Our frontend uses React with TypeScript for modern development
- The backend is built with FastAPI and Python for performance
- We use ChromaDB for vector storage and AI agent knowledge
- Authentication is handled with JWT tokens

{f"For {', '.join(topics)} specifically, these are implemented throughout our system with established patterns." if topics else ""}"""
        
        else:
            base_response = f"""I found some relevant information about your question in our ZeroDay codebase{' and your uploaded documents' if has_user_docs else ''}. The platform is built with modern technologies and follows established patterns for scalability and maintainability.

{f"Regarding {', '.join(topics)}, these are well-integrated throughout our system." if topics else ""}"""

        
        if user_docs:
            base_response += f"\n\n📄 **Referenced Documents:** {', '.join(user_docs[:3])}"
            if len(user_docs) > 3:
                base_response += f" and {len(user_docs) - 3} others"

        base_response += "\n\nCould you be more specific about what you'd like to know? I can provide details about implementation, configuration, or usage patterns."
        
        return base_response

    def _generate_suggestions_enhanced(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate enhanced suggestions based on context"""
        intent = context.get('intent', 'general')
        topics = context.get('topics', [])
        
        suggestions = []
        
        if intent == 'troubleshooting':
            suggestions.extend([
                "Check error logs and console output",
                "Review recent code changes",
                "Test in development environment"
            ])
        elif intent == 'how_to':
            suggestions.extend([
                "Check setup documentation",
                "Look at code examples",
                "Review configuration files"
            ])
        elif intent == 'document_specific':
            suggestions.extend([
                "Ask about specific sections in your documents",
                "Request analysis of uploaded content",
                "Compare information across documents"
            ])
        else:
            suggestions.extend([
                "Ask about specific implementation details",
                "Request code examples",
                "Check related documentation"
            ])
        
        if 'react' in topics:
            suggestions.append("Explore React component patterns")
        if 'authentication' in topics:
            suggestions.append("Review authentication flow")
        if 'api' in topics:
            suggestions.append("Check API endpoint documentation")
        if 'documents' in topics:
            suggestions.append("Analyze your uploaded documents")
        
        return suggestions[:4]

    def _create_helpful_response(self, message: str, user_id: str) -> Dict[str, Any]:
        """Create a helpful response structure"""
        return {
            "success": True,
            "response": message,
            "confidence": 0.8,
            "agent_type": "knowledge",
            "sources": [],
            "citations": [],
            "user_id": user_id,
            "llm_available": self.llm_initialized,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_stats(self, user_id: str = None, demo_mode: bool = None) -> Dict[str, Any]:
        """Get knowledge base statistics including user documents"""
        try:
            if demo_mode is None:
                demo_mode = self.demo_mode
                
            stats = self.db_setup.get_collection_stats() if hasattr(self, 'db_setup') else {}
            
            total_docs = sum(
                collection.get("count", 0) 
                for collection in stats.values() 
                if isinstance(collection, dict)
            )
            
         
            user_doc_count = 0
            if user_id and self.collections.get("main"):
                try:
                    user_results = self.collections["main"].query(
                        query_texts=[""],
                        n_results=1,
                        where={"user_id": user_id}
                    )
                    # This is a rough estimate - in production, implement proper counting
                    user_doc_count = len(user_results.get('documents', [[]])[0]) if user_results else 0
                except:
                    user_doc_count = 0
            
            status = "demo_ready" if demo_mode and total_docs > 0 else "demo_empty" if demo_mode else ("healthy" if total_docs > 0 else "empty")
            collection_name = "demo_collections" if demo_mode else self.config['vector_store']['collection_name']
            
            return {
                "total_documents": total_docs,
                "user_documents": user_doc_count,
                "collection_name": collection_name,
                "embedding_model": self.config['vector_store']['embedding_model'],
                "status": status,
                "user_id": user_id,
                "llm_available": self.llm_initialized,
                "llm_provider": self.llm_provider,
                "collections_detail": stats,
                "document_aware": True
            }
        except Exception as e:
            return {
                "total_documents": 0,
                "user_documents": 0,
                "collection_name": self.config['vector_store']['collection_name'],
                "status": f"error: {str(e)}",
                "user_id": user_id,
                "llm_available": self.llm_initialized,
                "document_aware": False
            }

if __name__ == "__main__":
    import asyncio
    
    async def test_document_aware_agent():
        print("=== Testing Document-Aware Knowledge Agent ===")
        
        try:
            agent = KnowledgeAgent()
            print(f" Agent created successfully")
            print(f"   LLM Available: {agent.llm_initialized}")
            print(f"   LLM Provider: {agent.llm_provider}")
            print(f"   Document-Aware: True")
            
           
            result = await agent.query("What is React?", "test_user")
            print(f"   General Query Success: {result['success']}")
            print(f"   Citations Available: {len(result.get('citations', []))}")
            
            
            doc_result = await agent.query("What does my uploaded document say about authentication?", "test_user")
            print(f"   Document Query Success: {doc_result['success']}")
            print(f"   Document Sources: {len(doc_result.get('document_sources', []))}")
            
        except Exception as e:
            print(f" Agent test failed: {e}")
    
    asyncio.run(test_document_aware_agent())