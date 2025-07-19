
import os
import yaml
import markdown
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from loguru import logger
from datetime import datetime
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, extract_file_metadata, sanitize_text
from dotenv import load_dotenv
load_dotenv()

class DocIngestor:
    
    def __init__(self, config_path: str = None, demo_mode: bool = False, user_id: str = None):
        self.config = self._load_config(config_path)
        self.demo_mode = demo_mode
        self.user_id = user_id or "demo_user"
        self.supported_extensions = {'.md', '.rst', '.txt', '.markdown', '.mkd'}
        self.markdown_parser = markdown.Markdown(extensions=[
            'toc', 'tables', 'fenced_code', 'codehilite'
        ])
        
        
        self._setup_document_patterns()
        
        if self.demo_mode:
            self.demo_config = self._load_demo_config()
            logger.info(f"DocIngestor initialized in DEMO mode for user: {self.user_id}")
        else:
            logger.info(f"DocIngestor initialized in REAL mode for user: {self.user_id}")
    
    def _setup_document_patterns(self):
        """Setup patterns for enhanced document analysis"""
        
        self.topic_patterns = {
            'getting_started': re.compile(r'getting\s+started|quick\s+start|installation|setup|introduction', re.IGNORECASE),
            'api_reference': re.compile(r'api|endpoint|reference|rest|graphql|swagger', re.IGNORECASE),
            'tutorial': re.compile(r'tutorial|walkthrough|step\s+by\s+step|guide|how\s+to', re.IGNORECASE),
            'troubleshooting': re.compile(r'troubleshoot|debug|error|problem|issue|faq', re.IGNORECASE),
            'architecture': re.compile(r'architecture|design|system|overview|structure', re.IGNORECASE),
            'deployment': re.compile(r'deploy|production|hosting|server|infrastructure', re.IGNORECASE),
            'testing': re.compile(r'test|testing|unit|integration|e2e|qa', re.IGNORECASE),
            'security': re.compile(r'security|auth|permission|token|encryption|ssl', re.IGNORECASE),
            'configuration': re.compile(r'config|settings|environment|variables|options', re.IGNORECASE),
            'examples': re.compile(r'example|sample|demo|snippet|code\s+example', re.IGNORECASE)
        }
        
        
        self.audience_patterns = {
            'beginner': re.compile(r'beginner|new|first\s+time|basic|intro|simple', re.IGNORECASE),
            'intermediate': re.compile(r'intermediate|moderate|standard|typical', re.IGNORECASE),
            'advanced': re.compile(r'advanced|expert|complex|detailed|in\s+depth', re.IGNORECASE),
            'developer': re.compile(r'developer|programmer|engineer|code|coding', re.IGNORECASE),
            'admin': re.compile(r'admin|administrator|sysadmin|devops|operations', re.IGNORECASE),
            'user': re.compile(r'user|end\s+user|customer|client|usage', re.IGNORECASE)
        }
        
        
        self.quality_indicators = {
            'boilerplate': [
                'lorem ipsum', 'placeholder', 'todo', 'fixme', 'coming soon',
                'under construction', 'work in progress', 'tbd', 'to be determined'
            ],
            'completeness': [
                'table of contents', 'prerequisites', 'examples', 'see also',
                'further reading', 'conclusion', 'summary'
            ]
        }
        
        
        self.semantic_boundaries = [
            r'\n\s*#{1,6}\s+',  
            r'\n\s*---+\s*\n',  
            r'\n\s*\*\*\*+\s*\n',  
            r'\n\s*```[a-zA-Z]*\n.*?\n```\s*\n',  
            r'\n\s*>\s+',  
            r'\n\s*\d+\.\s+',  
            r'\n\s*[-*+]\s+',  
        ]
        
       
        self.intent_patterns = {
            'explain': re.compile(r'explain|understand|what\s+is|definition|concept', re.IGNORECASE),
            'instruct': re.compile(r'how\s+to|steps|tutorial|guide|walkthrough', re.IGNORECASE),
            'reference': re.compile(r'reference|spec|documentation|manual|api', re.IGNORECASE),
            'troubleshoot': re.compile(r'troubleshoot|fix|solve|debug|error|problem', re.IGNORECASE),
            'compare': re.compile(r'compare|vs|versus|difference|alternative', re.IGNORECASE),
            'showcase': re.compile(r'example|demo|sample|showcase|illustration', re.IGNORECASE)
        }
        
    def _load_config(self, config_path: str = None) -> Dict:
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_demo_config(self) -> Dict:
        demo_config_path = os.path.join(
            os.path.dirname(__file__), "..", "configs", "demo_settings.yaml"
        )
        
        try:
            with open(demo_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("Demo config not found, using defaults")
            return {
                'demo_data_path': os.path.join(os.path.dirname(__file__), "..", "demo", "sample_data", "documents"),
                'scenarios': ['startup', 'enterprise', 'freelancer']
            }

    async def ingest_docs(self, base_path: str = None, scenario: str = None) -> List[Dict[str, Any]]:
        if self.demo_mode:
            return await self._ingest_demo_docs(scenario)
        else:
            return await self._ingest_real_docs(base_path)
    
    async def _ingest_demo_docs(self, scenario: str = None) -> List[Dict[str, Any]]:
        logger.info(f"Ingesting DEMO documentation for scenario: {scenario or 'default'}")
        
        demo_path = self.demo_config.get('demo_data_path')
        if not demo_path or not os.path.exists(demo_path):
            logger.warning("Demo documents not found, generating synthetic data")
            return self._generate_synthetic_docs(scenario)
        
        documents = await self._ingest_real_docs(demo_path)
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': True,
                'demo_scenario': scenario or 'default',
                'user_id': self.user_id,
                'demo_note': 'This is synthetic demo data for showcase purposes'
            })
        
        logger.info(f"Generated {len(documents)} DEMO documentation chunks")
        return documents
    
    async def _ingest_real_docs(self, base_path: str = None) -> List[Dict[str, Any]]:
        if not base_path:
            base_path = self.config['data_sources']['documentation']['path']
        
        base_path = Path(base_path).resolve()
        
        if not base_path.exists():
            logger.warning(f"Documentation path does not exist: {base_path}")
            return []
        
        logger.info(f"Starting enhanced documentation ingestion from: {base_path}")
        
        documents = []
        
        for file_path in self._walk_directory(base_path):
            try:
                if file_path.suffix.lower() in self.supported_extensions:
                    file_documents = await self._ingest_file(file_path, base_path)
                  
                    for doc in file_documents:
                        if self._validate_document_quality(doc):
                            enriched_doc = self._enrich_document(doc)
                            documents.append(enriched_doc)
                    
            except Exception as e:
                logger.error(f"Error ingesting file {file_path}: {str(e)}")
                continue
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': False,
                'user_id': self.user_id
            })
        
        logger.info(f"Ingested {len(documents)} enhanced documentation chunks from {base_path}")
        return documents
    
    def _validate_document_quality(self, doc: Dict[str, Any]) -> bool:
        """Validate document quality and filter out low-quality content"""
        content = doc.get('content', '').strip()
        metadata = doc.get('metadata', {})
        
 
        if len(content) < 50:
            return False
        
        
        content_lower = content.lower()
        for boilerplate in self.quality_indicators['boilerplate']:
            if boilerplate in content_lower and len(content) < 200:
                return False
        
    
        code_ratio = self._calculate_code_ratio(content)
        if code_ratio > 0.8 and len(content.split()) < 100:
            return False
        
      
        if metadata.get('section_title', '').strip() == '' and len(content) < 100:
            return False
        
        return True
    
    def _calculate_code_ratio(self, content: str) -> float:
        """Calculate the ratio of code to text content"""
        code_blocks = re.findall(r'```.*?```', content, re.DOTALL)
        inline_code = re.findall(r'`[^`]+`', content)
        
        total_code_length = sum(len(block) for block in code_blocks) + sum(len(code) for code in inline_code)
        total_length = len(content)
        
        return total_code_length / total_length if total_length > 0 else 0
    
    def _enrich_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Add enhanced metadata and LLM-friendly enrichment"""
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        
        
        enhanced_metadata = self._extract_enhanced_metadata(content, metadata)
        metadata.update(enhanced_metadata)
        
        
        quality_assessment = self._assess_document_quality(content, metadata)
        metadata['quality'] = quality_assessment
        
      
        llm_summary = self._create_document_summary(content, metadata)
        metadata['llm_summary'] = llm_summary
        
       
        semantic_info = self._extract_semantic_information(content)
        metadata['semantic'] = semantic_info
        
        return doc
    
    def _extract_enhanced_metadata(self, content: str, existing_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract enhanced metadata from document content"""
        enhanced = {}
        
        topic = self._infer_document_topic(content, existing_metadata)
        if topic:
            enhanced['inferred_topic'] = topic
        
       
        audience = self._infer_target_audience(content)
        if audience:
            enhanced['target_audience'] = audience
        
       
        intent = self._infer_document_intent(content)
        if intent:
            enhanced['document_intent'] = intent
        
        
        inferred_title = self._infer_document_title(content, existing_metadata)
        if inferred_title:
            enhanced['inferred_title'] = inferred_title
        
     
        structure_info = self._analyze_document_structure(content)
        enhanced['structure'] = structure_info
        
        
        prerequisites = self._extract_prerequisites(content)
        if prerequisites:
            enhanced['prerequisites'] = prerequisites
        
        return enhanced
    
    def _infer_document_topic(self, content: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Infer the main topic of the document"""
        title = metadata.get('section_title', '') + ' ' + metadata.get('inferred_title', '')
        full_text = (title + ' ' + content).lower()
        
        topic_scores = {}
        for topic, pattern in self.topic_patterns.items():
            matches = len(pattern.findall(full_text))
            if matches > 0:
                topic_scores[topic] = matches
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return None
    
    def _infer_target_audience(self, content: str) -> List[str]:
        """Infer the target audience for the document"""
        content_lower = content.lower()
        audiences = []
        
        for audience, pattern in self.audience_patterns.items():
            if pattern.search(content_lower):
                audiences.append(audience)
        
        return audiences[:3] 
    
    def _infer_document_intent(self, content: str) -> Optional[str]:
        """Infer the primary intent of the document"""
        content_lower = content.lower()
        
        intent_scores = {}
        for intent, pattern in self.intent_patterns.items():
            matches = len(pattern.findall(content_lower))
            if matches > 0:
                intent_scores[intent] = matches
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return None
    
    def _infer_document_title(self, content: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Infer a better document title if the current one is poor"""
        current_title = metadata.get('section_title', '')
        
        
        if current_title and len(current_title) > 5 and not current_title.lower() in ['introduction', 'section 1', 'full document']:
            return None
        
     
        lines = content.split('\n')
        for line in lines[:10]:  
            line = line.strip()
            if line.startswith('#'):
                title = re.sub(r'^#+\s*', '', line).strip()
                if len(title) > 5:
                    return title
        
        
        sentences = re.split(r'[.!?]', content.strip())
        if sentences:
            first_sentence = sentences[0].strip()
            if 10 <= len(first_sentence) <= 80 and not first_sentence.lower().startswith(('this', 'the', 'it', 'here')):
                return first_sentence
        
        return None
    
    def _analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structural elements of the document"""
        structure = {
            'has_headers': bool(re.search(r'^#+\s+', content, re.MULTILINE)),
            'header_count': len(re.findall(r'^#+\s+', content, re.MULTILINE)),
            'has_code_blocks': bool(re.search(r'```', content)),
            'code_block_count': len(re.findall(r'```.*?```', content, re.DOTALL)),
            'has_lists': bool(re.search(r'^\s*[-*+]\s+|^\s*\d+\.\s+', content, re.MULTILINE)),
            'has_tables': bool(re.search(r'\|.*\|', content)),
            'has_links': bool(re.search(r'\[.*?\]\(.*?\)', content)),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'estimated_reading_time': max(1, len(content.split()) // 200)  # ~200 WPM
        }
        
        return structure
    
    def _extract_prerequisites(self, content: str) -> List[str]:
        """Extract prerequisites mentioned in the document"""
        prerequisites = []
        
       
        prereq_patterns = [
            r'prerequisite[s]?:?\s*(.*?)(?:\n\n|\n#|\n---|\Z)',
            r'before\s+you\s+begin:?\s*(.*?)(?:\n\n|\n#|\n---|\Z)',
            r'requirements?:?\s*(.*?)(?:\n\n|\n#|\n---|\Z)',
            r'you\s+need:?\s*(.*?)(?:\n\n|\n#|\n---|\Z)'
        ]
        
        content_lower = content.lower()
        for pattern in prereq_patterns:
            matches = re.findall(pattern, content_lower, re.DOTALL | re.IGNORECASE)
            for match in matches:
                
                prereq_items = re.findall(r'[-*+]?\s*([^-*+\n]+)', match)
                prerequisites.extend([item.strip() for item in prereq_items if len(item.strip()) > 5])
        
        return prerequisites[:5]  
    
    def _assess_document_quality(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the overall quality of the document"""
        quality = {
            'score': 0,
            'issues': [],
            'strengths': []
        }
        
       
        completeness_score = 0
        for indicator in self.quality_indicators['completeness']:
            if indicator in content.lower():
                completeness_score += 1
                quality['strengths'].append(f'has_{indicator.replace(" ", "_")}')
        
        quality['score'] += min(completeness_score * 10, 30)  
        
        
        structure = metadata.get('structure', {})
        if structure.get('has_headers'):
            quality['score'] += 20
            quality['strengths'].append('well_structured')
        
        if structure.get('has_code_blocks'):
            quality['score'] += 10
            quality['strengths'].append('includes_examples')
        
        
        if len(content) < 100:
            quality['issues'].append('too_short')
            quality['score'] -= 20
        
        if len(content) > 5000:
            quality['issues'].append('very_long')
            quality['score'] -= 10
        
        
        content_lower = content.lower()
        for boilerplate in self.quality_indicators['boilerplate']:
            if boilerplate in content_lower:
                quality['issues'].append('contains_boilerplate')
                quality['score'] -= 15
                break
        
        
        avg_sentence_length = len(content.split()) / max(len(re.split(r'[.!?]', content)), 1)
        if avg_sentence_length > 30:
            quality['issues'].append('long_sentences')
            quality['score'] -= 5
        elif avg_sentence_length < 5:
            quality['issues'].append('very_short_sentences')
            quality['score'] -= 5
        else:
            quality['score'] += 10
            quality['strengths'].append('good_readability')
        
        quality['score'] = max(0, min(100, quality['score']))  
        return quality
    
    def _extract_semantic_information(self, content: str) -> Dict[str, Any]:
        """Extract semantic information for better understanding"""
        semantic = {}
        
        
        entities = self._extract_key_entities(content)
        if entities:
            semantic['key_entities'] = entities
        
       
        actions = self._extract_action_verbs(content)
        if actions:
            semantic['primary_actions'] = actions
        
    
        technologies = self._extract_technologies(content)
        if technologies:
            semantic['technologies'] = technologies
        
       
        complexity = self._assess_content_complexity(content)
        semantic['complexity_indicators'] = complexity
        
        return semantic
    
    def _extract_key_entities(self, content: str) -> List[str]:
        """Extract key entities mentioned in the document"""
       
        entities = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', content)
        
        
        code_terms = re.findall(r'`([^`]+)`', content)
        entities.extend(code_terms)
        
    
        filtered_entities = []
        common_words = {'The', 'This', 'That', 'You', 'We', 'They', 'It', 'And', 'Or', 'But', 'For', 'If', 'When'}
        
        for entity in entities:
            if entity not in common_words and len(entity) > 2:
                filtered_entities.append(entity)
        
     
        entity_counts = {}
        for entity in filtered_entities:
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
        
        return [entity for entity, count in sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    def _extract_action_verbs(self, content: str) -> List[str]:
        """Extract action verbs that indicate what the document helps you do"""
        action_patterns = [
            r'how\s+to\s+(\w+)',
            r'you\s+can\s+(\w+)',
            r'to\s+(\w+)\s+',
            r'will\s+(\w+)',
            r'should\s+(\w+)'
        ]
        
        actions = []
        content_lower = content.lower()
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content_lower)
            actions.extend(matches)
        
       
        action_words = ['create', 'build', 'setup', 'configure', 'install', 'deploy', 'test', 'debug', 'implement', 'use', 'run', 'start', 'stop', 'update', 'manage']
        filtered_actions = [action for action in actions if action in action_words]
        
        return list(set(filtered_actions))[:5]
    
    def _extract_technologies(self, content: str) -> List[str]:
        """Extract technology and framework mentions"""
        tech_patterns = {
            'languages': ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c++', 'c#', 'php', 'ruby'],
            'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'spring', 'rails'],
            'databases': ['postgresql', 'mysql', 'mongodb', 'redis', 'sqlite', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'tools': ['git', 'github', 'gitlab', 'jenkins', 'nginx', 'apache']
        }
        
        technologies = []
        content_lower = content.lower()
        
        for category, techs in tech_patterns.items():
            for tech in techs:
                if tech in content_lower:
                    technologies.append(tech)
        
        return list(set(technologies))
    
    def _assess_content_complexity(self, content: str) -> Dict[str, Any]:
        """Assess the complexity of the content"""
        complexity = {
            'technical_terms': 0,
            'code_density': 0,
            'conceptual_depth': 0
        }
    
        technical_indicators = ['api', 'algorithm', 'framework', 'library', 'module', 'function', 'method', 'class', 'object', 'interface']
        content_lower = content.lower()
        complexity['technical_terms'] = sum(1 for term in technical_indicators if term in content_lower)
        
       
        complexity['code_density'] = self._calculate_code_ratio(content)
        

        if len(content.split()) > 1000 and content.count('#') > 5:
            complexity['conceptual_depth'] = 'high'
        elif len(content.split()) > 300:
            complexity['conceptual_depth'] = 'medium'
        else:
            complexity['conceptual_depth'] = 'low'
        
        return complexity
    
    def _create_document_summary(self, content: str, metadata: Dict[str, Any]) -> str:
        """Create an LLM-friendly summary of the document"""
        title = metadata.get('inferred_title') or metadata.get('section_title', 'Untitled')
        topic = metadata.get('inferred_topic', 'general')
        intent = metadata.get('document_intent', 'inform')
        audience = metadata.get('target_audience', ['general'])
        
   
        summary_parts = [f"This is a {topic} document titled '{title}'"]
        
        if intent:
            summary_parts.append(f"with the primary intent to {intent}")
        
        if audience:
            audience_str = ', '.join(audience[:2])
            summary_parts.append(f"targeted at {audience_str} users")
        

        structure = metadata.get('structure', {})
        if structure.get('has_code_blocks'):
            summary_parts.append("and includes code examples")
        
        if structure.get('has_lists'):
            summary_parts.append("with structured lists")
        
    
        quality = metadata.get('quality', {})
        if quality.get('score', 0) > 70:
            summary_parts.append("The content is well-structured and comprehensive")
        
        
        reading_time = structure.get('estimated_reading_time', 1)
        summary_parts.append(f"with an estimated reading time of {reading_time} minute{'s' if reading_time != 1 else ''}")
        
        return '. '.join(summary_parts) + '.'
    
    def _enhanced_semantic_chunking(self, content: str) -> List[Dict[str, Any]]:
        """Create semantically meaningful chunks instead of just splitting by headers"""
        chunks = []
        

        header_sections = self._split_by_headers(content)
        
        for section in header_sections:
            section_content = section['content'].strip()
            if not section_content:
                continue
            
    
            if len(section_content.split()) > 300:
                sub_chunks = self._split_by_semantic_boundaries(section_content)
                for i, sub_chunk in enumerate(sub_chunks):
                    chunks.append({
                        'title': f"{section['title']} - Part {i+1}" if len(sub_chunks) > 1 else section['title'],
                        'level': section['level'],
                        'content': sub_chunk,
                        'start_line': section.get('start_line', 0),
                        'is_sub_chunk': len(sub_chunks) > 1,
                        'sub_chunk_index': i if len(sub_chunks) > 1 else None
                    })
            else:
                chunks.append(section)
        
        return chunks
    
    def _split_by_semantic_boundaries(self, content: str) -> List[str]:
        """Split content by semantic boundaries when it's too long"""
      
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if len(paragraphs) <= 2:
       
            sentences = re.split(r'[.!?]+\s+', content)
       
            chunks = []
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                sentence_length = len(sentence.split())
                if current_length + sentence_length > 150 and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_length = sentence_length
                else:
                    current_chunk.append(sentence)
                    current_length += sentence_length
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
        
       
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph_length = len(paragraph.split())
            
            
            if current_length + paragraph_length > 250 and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_length = paragraph_length
            else:
                current_chunk.append(paragraph)
                current_length += paragraph_length
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks

    def _generate_synthetic_docs(self, scenario: str = None) -> List[Dict[str, Any]]:
        synthetic_docs = [
            {
                'title': 'Getting Started Guide',
                'content': '''# Getting Started with ZeroDay Platform

    Welcome to ZeroDay. This is a placeholder for demo purposes.
    ''',
                'tags': ['getting-started'],
                'difficulty': 'beginner'
            }
        ]

        documents = []
        for i, doc_data in enumerate(synthetic_docs):
            sections = self._enhanced_semantic_chunking(doc_data['content'])

            for section in sections:
                if not section['content'].strip():
                    continue

                clean_content = sanitize_text(section['content'])

                doc = {
                    'content': clean_content,
                    'metadata': {
                        'source_type': 'documentation',
                        'file_path': f"{doc_data['title'].lower().replace(' ', '_')}.md",
                        'section_title': section['title'],
                        'section_level': section['level'],
                        'file_size': len(clean_content),
                        'created_at': datetime.now().isoformat(),
                        'modified_at': datetime.now().isoformat(),
                        'content_hash': get_file_hash(clean_content),
                        'tags': doc_data['tags'],
                        'difficulty': doc_data['difficulty'],
                        'doc_type': 'markdown',
                        'keywords': self._extract_keywords(clean_content),
                        'is_demo': True,
                        'demo_scenario': scenario or 'default',
                        'user_id': self.user_id,
                        'demo_note': 'This is synthetic demo data for showcase purposes'
                    }
                }

                enriched_doc = self._enrich_document(doc)
                documents.append(enriched_doc)

        logger.info(f"Generated {len(documents)} enhanced synthetic documentation chunks")
        return documents

    
    def _walk_directory(self, base_path: Path) -> List[Path]:
        files = []
        
        for root, dirs, filenames in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                if file_path.suffix.lower() in self.supported_extensions:
                    files.append(file_path)
        
        return files
    
    async def _ingest_file(self, file_path: Path, base_path: Path) -> List[Dict[str, Any]]:
        try:
            relative_path = file_path.relative_to(base_path)
            file_metadata = extract_file_metadata(file_path)
            file_extension = file_path.suffix.lower()

            # Handle JSON separately
            if file_extension == '.json':
                try:
                    import json
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)

                    content = json.dumps(json_data, indent=2)

                    return [{
                        "content": sanitize_text(content),
                        "metadata": {
                            "source_type": "documentation",
                            "file_path": str(relative_path),
                            "file_size": file_metadata['size'],
                            "created_at": file_metadata['created_at'],
                            "modified_at": file_metadata['modified_at'],
                            "content_hash": get_file_hash(content),
                            "tags": ['json'],
                            "difficulty": 'intermediate',
                            "doc_type": 'json',
                            "user_id": self.user_id
                        }
                    }]
                except Exception as json_err:
                    logger.error(f"Error processing JSON file {file_path}: {json_err}")
                    return []

            # For all other text-based files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return []

            if file_extension in {'.md', '.markdown', '.mkd'}:
                return self._parse_markdown(content, str(relative_path), file_metadata)
            elif file_extension == '.rst':
                return self._parse_rst(content, str(relative_path), file_metadata)
            else:
                return self._parse_text(content, str(relative_path), file_metadata)

        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {str(e)}")
            return []

    
    def _parse_markdown(self, content: str, file_path: str, file_metadata: Dict) -> List[Dict[str, Any]]:
        documents = []
        
        frontmatter = self._extract_frontmatter(content)
        if frontmatter:
            content = content[frontmatter['end_pos']:]
        
      
        sections = self._enhanced_semantic_chunking(content)
        
        for section in sections:
            if not section['content'].strip():
                continue
            
            clean_content = sanitize_text(section['content'])
            code_blocks = self._extract_code_blocks(section['content'])
            links = self._extract_links(section['content'])
            
            doc = {
                'content': clean_content,
                'metadata': {
                    'source_type': 'documentation',
                    'file_path': file_path,
                    'section_title': section['title'],
                    'section_level': section['level'],
                    'file_size': file_metadata['size'],
                    'created_at': file_metadata['created_at'],
                    'modified_at': file_metadata['modified_at'],
                    'content_hash': get_file_hash(clean_content),
                    'tags': self._extract_tags(section['content'], frontmatter),
                    'difficulty': self._estimate_difficulty(clean_content),
                    'doc_type': 'markdown',
                    'code_blocks': len(code_blocks),
                    'external_links': len(links),
                    'frontmatter': frontmatter.get('data', {}) if frontmatter else {},
                    'keywords': self._extract_keywords(clean_content),
                   
                    'is_sub_chunk': section.get('is_sub_chunk', False),
                    'sub_chunk_index': section.get('sub_chunk_index'),
                    'code_block_details': code_blocks,
                    'link_details': links
                }
            }
            documents.append(doc)
        
        return documents
    
    def _parse_rst(self, content: str, file_path: str, file_metadata: Dict) -> List[Dict[str, Any]]:
       
        sections = self._enhanced_semantic_chunking(content)
        documents = []
        
        for section in sections:
            if not section['content'].strip():
                continue
            
            clean_content = sanitize_text(section['content'])
            
            doc = {
                'content': clean_content,
                'metadata': {
                    'source_type': 'documentation',
                    'file_path': file_path,
                    'section_title': section['title'],
                    'section_level': section['level'],
                    'file_size': file_metadata['size'],
                    'created_at': file_metadata['created_at'],
                    'modified_at': file_metadata['modified_at'],
                    'content_hash': get_file_hash(clean_content),
                    'tags': self._extract_tags(section['content']),
                    'difficulty': self._estimate_difficulty(clean_content),
                    'doc_type': 'rst',
                    'keywords': self._extract_keywords(clean_content),
                   
                    'is_sub_chunk': section.get('is_sub_chunk', False),
                    'sub_chunk_index': section.get('sub_chunk_index')
                }
            }
            documents.append(doc)
        
        return documents
    
    def _parse_text(self, content: str, file_path: str, file_metadata: Dict) -> List[Dict[str, Any]]:
        
        chunks = self._split_by_semantic_boundaries(content)
        documents = []
        
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            
            clean_content = sanitize_text(chunk)
            
            doc = {
                'content': clean_content,
                'metadata': {
                    'source_type': 'documentation',
                    'file_path': file_path,
                    'section_title': f"Section {i+1}",
                    'section_level': 1,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_size': file_metadata['size'],
                    'created_at': file_metadata['created_at'],
                    'modified_at': file_metadata['modified_at'],
                    'content_hash': get_file_hash(clean_content),
                    'tags': self._extract_tags(chunk),
                    'difficulty': self._estimate_difficulty(clean_content),
                    'doc_type': 'text',
                    'keywords': self._extract_keywords(clean_content),
                    
                    'is_semantic_chunk': True
                }
            }
            documents.append(doc)
        
        return documents
    
    def _extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        if not content.startswith('---'):
            return None
        
        try:
            end_marker = content.find('\n---\n', 4)
            if end_marker == -1:
                return None
            
            frontmatter_text = content[4:end_marker]
            frontmatter_data = yaml.safe_load(frontmatter_text)
            
            return {
                'data': frontmatter_data,
                'end_pos': end_marker + 5
            }
        except Exception as e:
            logger.warning(f"Error parsing frontmatter: {str(e)}")
            return None
    
    def _split_by_headers(self, content: str) -> List[Dict[str, Any]]:
        lines = content.split('\n')
        sections = []
        current_section = {
            'title': 'Introduction',
            'level': 1,
            'content': '',
            'start_line': 0
        }

        found_header = False

        for i, line in enumerate(lines):
            match = re.match(r'^(#{1,6})\s+(.*)', line.strip())
            if match:
                found_header = True
                if current_section['content'].strip():
                    sections.append(current_section)
                level = len(match.group(1))
                title = match.group(2).strip()
                current_section = {
                    'title': title,
                    'level': level,
                    'content': '',
                    'start_line': i
                }
            else:
                current_section['content'] += line + '\n'

        if current_section['content'].strip():
            sections.append(current_section)

        
        if not found_header and content.strip():
            return [{
                'title': 'Full Document',
                'level': 1,
                'content': content,
                'start_line': 0
            }]

        return sections

    
    def _split_rst_by_headers(self, content: str) -> List[Dict[str, Any]]:
        sections = []
        lines = content.split('\n')
        
        current_section = {
            'title': 'Introduction',
            'level': 0,
            'content': '',
            'start_line': 0
        }
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                
                if re.match(r'^[=\-`:\'"~^_*+#<>]{3,}', next_line) and len(next_line) >= len(line.strip()):
                
                    if current_section['content'].strip():
                        sections.append(current_section)
                    
                    char = next_line[0]
                    level_map = {'=': 1, '-': 2, '`': 3, ':': 4, "'": 5, '"': 6, '~': 7, '^': 8, '_': 9, '*': 10, '+': 11, '#': 12}
                    level = level_map.get(char, 1)
                    
                    current_section = {
                        'title': line.strip(),
                        'level': level,
                        'content': '',
                        'start_line': i
                    }
                    
                    i += 2
                    continue
            
            current_section['content'] += line + '\n'
            i += 1

        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _chunk_text(self, content: str, max_chunk_size: int = 1000) -> List[str]:
        if len(content) <= max_chunk_size:
            return [content]
        
        chunks = []
        paragraphs = content.split('\n\n')
        
        current_chunk = ''
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= max_chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        code_blocks = []
        
        fenced_pattern = r'```(\w+)?\n(.*?)```'
        for match in re.finditer(fenced_pattern, content, re.DOTALL):
            language = match.group(1) or 'unknown'
            code = match.group(2).strip()
            code_blocks.append({
                'language': language,
                'code': code,
                'type': 'fenced'
            })

        indented_pattern = r'\n((?:    .*\n?)+)'
        for match in re.finditer(indented_pattern, content):
            code = match.group(1).strip()
            code = '\n'.join(line[4:] if line.startswith('    ') else line for line in code.split('\n'))
            code_blocks.append({
                'language': 'unknown',
                'code': code,
                'type': 'indented'
            })
        
        return code_blocks
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        links = []
        
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            is_external = url.startswith(('http://', 'https://'))
            links.append({
                'text': text,
                'url': url,
                'type': 'markdown',
                'is_external': is_external
            })

        ref_pattern = r'\[([^\]]+)\]\[([^\]]+)\]'
        for match in re.finditer(ref_pattern, content):
            text = match.group(1)
            ref = match.group(2)
            links.append({
                'text': text,
                'reference': ref,
                'type': 'reference',
                'is_external': False
            })
        
        return links
    
    def _extract_tags(self, content: str, frontmatter: Dict = None) -> List[str]:
        tags = []
        
        if frontmatter and 'data' in frontmatter:
            fm_data = frontmatter['data']
            if 'tags' in fm_data:
                tags.extend(fm_data['tags'] if isinstance(fm_data['tags'], list) else [fm_data['tags']])
            if 'keywords' in fm_data:
                tags.extend(fm_data['keywords'] if isinstance(fm_data['keywords'], list) else [fm_data['keywords']])
            if 'category' in fm_data:
                tags.append(fm_data['category'])
        
        tech_terms = [
            'api', 'rest', 'graphql', 'database', 'sql', 'nosql', 'docker', 'kubernetes',
            'react', 'vue', 'angular', 'node', 'python', 'javascript', 'typescript',
            'git', 'github', 'deployment', 'testing', 'authentication', 'authorization',
            'microservices', 'serverless', 'cloud', 'aws', 'azure', 'gcp'
        ]
        
        content_lower = content.lower()
        for term in tech_terms:
            if term in content_lower:
                tags.append(term)
        
        code_terms = re.findall(r'`([^`]+)`', content)
        tags.extend([term for term in code_terms if len(term) > 2 and len(term) < 20])
        
        return list(set(tags))
    
    def _extract_keywords(self, content: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were',
            'said', 'each', 'which', 'their', 'time', 'would', 'there', 'could',
            'other', 'more', 'very', 'what', 'know', 'just', 'first', 'into', 'over',
            'think', 'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should',
            'after', 'being', 'now', 'made', 'before', 'through', 'when', 'where',
            'much', 'good', 'well', 'such', 'most', 'some', 'many', 'even', 'back',
            'come', 'these', 'than', 'them', 'want', 'here', 'does', 'about'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:10]]
    
    def _estimate_difficulty(self, content: str) -> str:
        difficulty_score = 0
        
        tech_terms = ['api', 'algorithm', 'architecture', 'framework', 'implementation', 'configuration']
        difficulty_score += sum(1 for term in tech_terms if term in content.lower())
        
        complex_patterns = ['async', 'promise', 'callback', 'closure', 'inheritance', 'polymorphism']
        difficulty_score += sum(1 for pattern in complex_patterns if pattern in content.lower())
        
        word_count = len(content.split())
        if word_count > 500:
            difficulty_score += 2
        elif word_count > 200:
            difficulty_score += 1
        
        code_blocks = len(re.findall(r'```.*?```', content, re.DOTALL))
        difficulty_score += code_blocks
        
        if difficulty_score < 3:
            return 'beginner'
        elif difficulty_score < 8:
            return 'intermediate'
        else:
            return 'advanced'
    
    async def ingest_single_file(self, file_path: str) -> List[Dict[str, Any]]:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return []
        
        if file_path.suffix.lower() not in self.supported_extensions:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return []
        
        return await self._ingest_file(file_path, file_path.parent)
    
    def set_demo_mode(self, demo_mode: bool, scenario: str = None) -> None:
        self.demo_mode = demo_mode
        if demo_mode:
            logger.info(f"Switched to DEMO mode with scenario: {scenario or 'default'}")
        else:
            logger.info("Switched to REAL mode")
    
    def get_demo_scenarios(self) -> List[str]:
        if hasattr(self, 'demo_config'):
            return self.demo_config.get('scenarios', ['startup', 'enterprise', 'freelancer'])
        return ['startup', 'enterprise', 'freelancer']
    
    def get_supported_formats(self) -> List[str]:
        return list(self.supported_extensions)
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        return {
            "supported_extensions": list(self.supported_extensions),
            "markdown_extensions": ['toc', 'tables', 'fenced_code', 'codehilite'],
            "demo_mode": self.demo_mode,
            "user_id": self.user_id,
            "demo_scenarios": self.get_demo_scenarios() if self.demo_mode else None,
            "features": [
                "frontmatter_extraction",
                "enhanced_semantic_chunking", 
                "code_block_detection",
                "link_extraction",
                "keyword_extraction",
                "difficulty_estimation",
                "quality_assessment",
                "topic_inference",
                "audience_detection",
                "intent_analysis",
                "llm_optimization"
            ],
            "enhanced_capabilities": {
                "semantic_chunking": True,
                "quality_validation": True,
                "metadata_enrichment": True,
                "topic_detection": True,
                "audience_inference": True,
                "intent_analysis": True,
                "complexity_assessment": True,
                "llm_summaries": True
            }
        }


def ingest_docs_quick(base_path: str = None, demo_mode: bool = False, user_id: str = None, scenario: str = None) -> List[Dict[str, Any]]:
    ingestor = DocIngestor(demo_mode=demo_mode, user_id=user_id)
    import asyncio
    return asyncio.run(ingestor.ingest_docs(base_path, scenario))

def ingest_single_doc(file_path: str, demo_mode: bool = False, user_id: str = None) -> List[Dict[str, Any]]:
    ingestor = DocIngestor(demo_mode=demo_mode, user_id=user_id)
    import asyncio
    return asyncio.run(ingestor.ingest_single_file(file_path))

if __name__ == "__main__":
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            demo_mode = '--demo' in sys.argv
            user_id = None
            scenario = None
            
            for i, arg in enumerate(sys.argv):
                if arg == '--user' and i + 1 < len(sys.argv):
                    user_id = sys.argv[i + 1]
                elif arg == '--scenario' and i + 1 < len(sys.argv):
                    scenario = sys.argv[i + 1]
            
            ingestor = DocIngestor(demo_mode=demo_mode, user_id=user_id)
            
            if command == "ingest":
                base_path = None
                for arg in sys.argv[2:]:
                    if not arg.startswith('--') and arg not in [user_id, scenario]:
                        base_path = arg
                        break
                
                results = await ingestor.ingest_docs(base_path, scenario)
                print(f"Ingested {len(results)} enhanced documentation chunks")
                
                if demo_mode:
                    print(f"Demo mode: {demo_mode}, Scenario: {scenario or 'default'}")
                
                for i, result in enumerate(results[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"Type: {result['metadata']['doc_type']}")
                    print(f"Title: {result['metadata']['section_title']}")
                    print(f"File: {result['metadata']['file_path']}")
                    print(f"Difficulty: {result['metadata']['difficulty']}")
                    print(f"Demo: {result['metadata'].get('is_demo', False)}")
                    
                   
                    if 'inferred_topic' in result['metadata']:
                        print(f"Topic: {result['metadata']['inferred_topic']}")
                    if 'target_audience' in result['metadata']:
                        print(f"Audience: {', '.join(result['metadata']['target_audience'])}")
                    if 'quality' in result['metadata']:
                        quality = result['metadata']['quality']
                        print(f"Quality Score: {quality.get('score', 0)}/100")
                    if 'llm_summary' in result['metadata']:
                        print(f"Summary: {result['metadata']['llm_summary'][:100]}...")
                    
                    print(f"Content: {result['content'][:100]}...")
                    
            elif command == "file":
                if len(sys.argv) < 3:
                    print("Usage: python doc_ingestor.py file <file_path>")
                    return
                    
                file_path = None
                for arg in sys.argv[2:]:
                    if not arg.startswith('--') and arg not in [user_id, scenario]:
                        file_path = arg
                        break
                
                if not file_path:
                    print("Error: No file path provided")
                    return
                    
                results = await ingestor.ingest_single_file(file_path)
                print(f"Ingested {len(results)} enhanced chunks from {file_path}")
                
                for result in results:
                    print(f"Section: {result['metadata']['section_title']}")
                    print(f"Tags: {result['metadata']['tags']}")
                    print(f"Keywords: {result['metadata']['keywords']}")
                    print(f"Enhanced fields: {list(result['metadata'].keys())}")
                    
            elif command == "demo":
                print("Available demo scenarios:")
                for scenario in ingestor.get_demo_scenarios():
                    print(f"  - {scenario}")
                    
            elif command == "stats":
                stats = ingestor.get_ingestion_stats()
                print("Enhanced Documentation Ingestor Statistics:")
                print(json.dumps(stats, indent=2))
                
            else:
                print("Available commands:")
                print("  ingest [path] [--demo] [--user USER_ID] [--scenario SCENARIO] - Ingest documentation with enhancements")
                print("  file <file_path> [--demo] [--user USER_ID] - Ingest single documentation file with enhancements")
                print("  demo - Show available demo scenarios")
                print("  stats - Show enhanced ingestor capabilities")
        else:
            print("Usage: python doc_ingestor.py [ingest|file|demo|stats] [options...]")
            print("Options:")
            print("  --demo              Enable demo mode")
            print("  --user USER_ID      Set user ID")
            print("  --scenario NAME     Set demo scenario (startup/enterprise/freelancer)")
            print("\nEnhanced Features:")
            print("  ✓ Semantic chunking by content meaning")
            print("  ✓ Quality validation and filtering")
            print("  ✓ Topic and audience inference")
            print("  ✓ Intent analysis and complexity assessment")
            print("  ✓ LLM-optimized summaries and metadata")
            print("  ✓ Enhanced code block and link extraction")
    
    asyncio.run(main())
                