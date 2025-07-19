import os
import yaml
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from loguru import logger
import asyncio
import sys
import re
import hashlib
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .code_parser import CodeParser
from .doc_ingestor import DocIngestor
from .pr_fetcher import PRFetcher
from .slack_parser import SlackParser
from .ticket_fetcher import TicketFetcher
from .synthetic_data_generator import SyntheticDataGenerator
from .demo_github import DemoGitHub
from .demo_slack import DemoSlack
from .demo_jira import DemoJira
from dotenv import load_dotenv
load_dotenv()

class IntegrationManager:
    
    def __init__(self, config_path: str = None, demo_mode: bool = False, user_id: str = None):
        self.config = self._load_config(config_path)
        self.demo_mode = demo_mode
        self.user_id = user_id or "demo_user"
        self.scenario = None
        
        
        self._setup_integration_patterns()
        
        self._initialize_components()
        
        logger.info(f"IntegrationManager initialized in {'DEMO' if demo_mode else 'REAL'} mode for user: {self.user_id}")
    
    def _setup_integration_patterns(self):
        """Setup patterns for analyzing relationships between data sources"""
        
        self.relationship_patterns = {
            'supports': {
                'patterns': [
                    r'support[s]?|implement[s]?|provide[s]?|enable[s]?',
                    r'used\s+by|required\s+by|needed\s+for'
                ],
                'strength': 0.8
            },
            'extends': {
                'patterns': [
                    r'extend[s]?|inherit[s]?|build[s]?\s+on|based\s+on',
                    r'derived\s+from|subclass|override[s]?'
                ],
                'strength': 0.9
            },
            'explains': {
                'patterns': [
                    r'explain[s]?|describe[s]?|document[s]?|detail[s]?',
                    r'how\s+to|guide|tutorial|example\s+of'
                ],
                'strength': 0.7
            },
            'tests': {
                'patterns': [
                    r'test[s]?|spec|verify|validate|assert',
                    r'should|expect|mock|stub'
                ],
                'strength': 0.9
            },
            'contradicts': {
                'patterns': [
                    r'contradict[s]?|conflict[s]?|inconsistent|mismatch',
                    r'deprecated|obsolete|outdated'
                ],
                'strength': 0.6
            },
            'references': {
                'patterns': [
                    r'reference[s]?|refer[s]?\s+to|mention[s]?|cite[s]?',
                    r'see\s+also|related\s+to|link[s]?\s+to'
                ],
                'strength': 0.5
            }
        }
        
        
        self.quality_indicators = {
            'freshness': {
                'recent': 0.9,    
                'moderate': 0.7,  
                'stale': 0.4,     
                'very_stale': 0.2 
            },
            'completeness': {
                'complete': 0.9,
                'partial': 0.6,
                'incomplete': 0.3
            },
            'consistency': {
                'consistent': 0.9,
                'minor_issues': 0.7,
                'major_issues': 0.4,
                'inconsistent': 0.2
            }
        }
        
        
        self.issue_patterns = {
            'stale_content': r'(todo|fixme|temporary|hack|workaround)',
            'missing_documentation': r'(undocumented|no\s+docs?|missing\s+docs?)',
            'broken_links': r'(broken\s+link|dead\s+link|404|not\s+found)',
            'version_mismatch': r'(version\s+mismatch|incompatible|deprecated)',
            'incomplete_implementation': r'(not\s+implemented|placeholder|stub)'
        }
        
        
        self.semantic_extractors = {
            'code_to_docs': self._extract_code_doc_context,
            'test_to_code': self._extract_test_code_context,
            'ticket_to_code': self._extract_ticket_code_context,
            'pr_to_code': self._extract_pr_code_context,
            'conversation_to_all': self._extract_conversation_context
        }
    
    def _load_config(self, config_path: str = None) -> Dict:
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {'data_sources': {}}
    
    def _initialize_components(self):
        self.code_parser = CodeParser(demo_mode=self.demo_mode, user_id=self.user_id)
        self.doc_ingestor = DocIngestor(demo_mode=self.demo_mode, user_id=self.user_id)
        self.pr_fetcher = PRFetcher(demo_mode=self.demo_mode, user_id=self.user_id)
        self.slack_parser = SlackParser(demo_mode=self.demo_mode, user_id=self.user_id)
        self.ticket_fetcher = TicketFetcher(demo_mode=self.demo_mode, user_id=self.user_id)
        
        if self.demo_mode:
            self.synthetic_generator = SyntheticDataGenerator(user_id=self.user_id)
            self.demo_github = DemoGitHub(user_id=self.user_id)
            self.demo_slack = DemoSlack(user_id=self.user_id)
            self.demo_jira = DemoJira(user_id=self.user_id)
    
    def set_demo_mode(self, demo_mode: bool, scenario: str = None):
        self.demo_mode = demo_mode
        self.scenario = scenario
        
        for component in [self.code_parser, self.doc_ingestor, self.pr_fetcher, 
                         self.slack_parser, self.ticket_fetcher]:
            component.set_demo_mode(demo_mode, scenario)
        
        if demo_mode and not hasattr(self, 'synthetic_generator'):
            self.synthetic_generator = SyntheticDataGenerator(user_id=self.user_id)
            self.demo_github = DemoGitHub(user_id=self.user_id)
            self.demo_slack = DemoSlack(user_id=self.user_id)
            self.demo_jira = DemoJira(user_id=self.user_id)
        
        logger.info(f"Switched to {'DEMO' if demo_mode else 'REAL'} mode with scenario: {scenario or 'default'}")
    
    async def ingest_all_data_sources(self, scenario: str = None) -> Dict[str, List[Dict[str, Any]]]:
        scenario = scenario or self.scenario or 'startup'
        
        if self.demo_mode:
            results = await self._ingest_demo_data(scenario)
        else:
            results = await self._ingest_real_data()
        
        
        enriched_results = await self._analyze_integrations(results)
        
        return enriched_results
    
    async def _ingest_demo_data(self, scenario: str) -> Dict[str, List[Dict[str, Any]]]:
        logger.info(f"Ingesting all demo data sources for scenario: {scenario}")
        
        results = {}
        
        try:
            results['code'] = await self.code_parser.parse_codebase(scenario=scenario)
            logger.info(f"Code: {len(results['code'])} documents")
        except Exception as e:
            logger.error(f"Code parsing failed: {e}")
            results['code'] = []
        
        try:
            results['documents'] = await self.doc_ingestor.ingest_docs(scenario=scenario)
            logger.info(f"Documents: {len(results['documents'])} documents")
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            results['documents'] = []
        
        try:
            results['pull_requests'] = await self.pr_fetcher.fetch_pull_requests(scenario=scenario)
            logger.info(f"Pull Requests: {len(results['pull_requests'])} documents")
        except Exception as e:
            logger.error(f"PR fetching failed: {e}")
            results['pull_requests'] = []
        
        try:
            results['conversations'] = await self.slack_parser.parse_slack_export(scenario=scenario)
            logger.info(f"Conversations: {len(results['conversations'])} documents")
        except Exception as e:
            logger.error(f"Slack parsing failed: {e}")
            results['conversations'] = []
        
        try:
            results['tickets'] = await self.ticket_fetcher.fetch_tickets(scenario=scenario)
            logger.info(f"Tickets: {len(results['tickets'])} documents")
        except Exception as e:
            logger.error(f"Ticket fetching failed: {e}")
            results['tickets'] = []
        
        total_documents = sum(len(docs) for docs in results.values())
        logger.info(f"Total demo documents ingested: {total_documents}")
        
        return results
    
    async def _ingest_real_data(self) -> Dict[str, List[Dict[str, Any]]]:
        logger.info("Ingesting all real data sources")
        
        results = {}
        
        try:
            results['code'] = await self.code_parser.parse_codebase()
            logger.info(f"Code: {len(results['code'])} documents")
        except Exception as e:
            logger.error(f"Code parsing failed: {e}")
            results['code'] = []
        
        try:
            results['documents'] = await self.doc_ingestor.ingest_docs()
            logger.info(f"Documents: {len(results['documents'])} documents")
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            results['documents'] = []
        
        try:
            repo_url = self.config.get('data_sources', {}).get('github', {}).get('repo_url')
            results['pull_requests'] = await self.pr_fetcher.fetch_pull_requests(repo_url)
            logger.info(f"Pull Requests: {len(results['pull_requests'])} documents")
        except Exception as e:
            logger.error(f"PR fetching failed: {e}")
            results['pull_requests'] = []
        
        try:
            export_path = self.config.get('data_sources', {}).get('slack_export', {}).get('path')
            results['conversations'] = await self.slack_parser.parse_slack_export(export_path)
            logger.info(f"Conversations: {len(results['conversations'])} documents")
        except Exception as e:
            logger.error(f"Slack parsing failed: {e}")
            results['conversations'] = []
        
        try:
            results['tickets'] = await self.ticket_fetcher.fetch_tickets(source='jira')
            logger.info(f"Tickets: {len(results['tickets'])} documents")
        except Exception as e:
            logger.error(f"Ticket fetching failed: {e}")
            results['tickets'] = []
        
        total_documents = sum(len(docs) for docs in results.values())
        logger.info(f"Total real documents ingested: {total_documents}")
        
        return results
    
    async def _analyze_integrations(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze integrations between different data sources"""
        logger.info("Analyzing integrations between data sources")
        
        
        integration_map = self._create_integration_map(results)
        
        
        for source_type, documents in results.items():
            for doc in documents:
                
                integration_analysis = self._analyze_document_integration(doc, integration_map, source_type)
                doc['metadata']['integration'] = integration_analysis
        
        
        global_integration = self._create_global_integration_summary(results, integration_map)
        
        
        results['_integration_summary'] = global_integration
        
        return results
    
    def _create_integration_map(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Create a mapping of all content for cross-reference analysis"""
        integration_map = {
            'content_index': {},
            'file_index': {},
            'term_index': {},
            'timestamp_index': {}
        }
        
        for source_type, documents in results.items():
            for doc in documents:
                content = doc.get('content', '').lower()
                metadata = doc.get('metadata', {})
                
                
                doc_id = self._generate_doc_id(doc, source_type)
                integration_map['content_index'][doc_id] = {
                    'source': source_type,
                    'content': content,
                    'metadata': metadata,
                    'terms': self._extract_terms(content)
                }
                
               
                file_path = metadata.get('file_path', '')
                if file_path:
                    if file_path not in integration_map['file_index']:
                        integration_map['file_index'][file_path] = []
                    integration_map['file_index'][file_path].append(doc_id)
                
                
                terms = self._extract_terms(content)
                for term in terms:
                    if term not in integration_map['term_index']:
                        integration_map['term_index'][term] = []
                    integration_map['term_index'][term].append(doc_id)
                
                
                timestamp = metadata.get('created_at') or metadata.get('modified_at')
                if timestamp:
                    try:
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        date_key = date.strftime('%Y-%m-%d')
                        if date_key not in integration_map['timestamp_index']:
                            integration_map['timestamp_index'][date_key] = []
                        integration_map['timestamp_index'][date_key].append(doc_id)
                    except:
                        pass
        
        return integration_map
    
    def _generate_doc_id(self, doc: Dict[str, Any], source_type: str) -> str:
        """Generate a unique document ID"""
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        
        
        file_path = metadata.get('file_path', '')
        name = metadata.get('name', '')
        
        if file_path and name:
            identifier = f"{source_type}:{file_path}:{name}"
        elif file_path:
            identifier = f"{source_type}:{file_path}"
        else:
           
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            identifier = f"{source_type}:{content_hash}"
        
        return identifier
    
    def _extract_terms(self, content: str) -> List[str]:
        """Extract meaningful terms from content"""
        
        terms = []
        
        
        code_terms = re.findall(r'\b[A-Z][a-zA-Z0-9]*\b|\b[a-z][a-z0-9_]*[a-z0-9]\b', content)
        terms.extend(code_terms)
        
        
        file_terms = re.findall(r'\b\w+\.\w+\b|/[\w/]+\b', content)
        terms.extend(file_terms)
        
        
        tech_terms = re.findall(r'\b(?:api|test|function|class|method|endpoint|service|component|module)\w*\b', content, re.IGNORECASE)
        terms.extend(tech_terms)
        
        
        filtered_terms = [term for term in terms if len(term) > 3 and len(term) < 50]
        return list(set(filtered_terms))
    
    def _analyze_document_integration(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Analyze integration for a single document"""
        integration_analysis = {
            'quality_score': 0.0,
            'relationships': [],
            'issues': [],
            'semantic_context': {},
            'llm_summary': ''
        }
        
        content = doc.get('content', '').lower()
        metadata = doc.get('metadata', {})
        doc_id = self._generate_doc_id(doc, source_type)
        
       
        quality_score = self._calculate_integration_quality(doc, integration_map, source_type)
        integration_analysis['quality_score'] = quality_score
        
        
        relationships = self._find_relationships(doc, integration_map, source_type)
        integration_analysis['relationships'] = relationships
        
       
        issues = self._detect_integration_issues(doc, integration_map, source_type)
        integration_analysis['issues'] = issues
        
        
        semantic_context = self._extract_semantic_context(doc, integration_map, source_type)
        integration_analysis['semantic_context'] = semantic_context
        
        
        llm_summary = self._create_integration_summary(doc, integration_analysis, source_type)
        integration_analysis['llm_summary'] = llm_summary
        
        return integration_analysis
    
    def _calculate_integration_quality(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> float:
        """Calculate integration quality score (0.0 to 1.0)"""
        quality_score = 0.0
        factors = []
        
        metadata = doc.get('metadata', {})
        content = doc.get('content', '')
        
       
        freshness_score = self._calculate_freshness_score(metadata)
        factors.append(('freshness', freshness_score, 0.3))
        
        
        cross_ref_score = self._calculate_cross_reference_score(doc, integration_map, source_type)
        factors.append(('cross_reference', cross_ref_score, 0.3))
        
       
        completeness_score = self._calculate_completeness_score(doc, source_type)
        factors.append(('completeness', completeness_score, 0.2))
        
        
        consistency_score = self._calculate_consistency_score(doc, integration_map, source_type)
        factors.append(('consistency', consistency_score, 0.2))
        
        
        total_weight = sum(weight for _, _, weight in factors)
        for factor_name, score, weight in factors:
            quality_score += (score * weight) / total_weight
        
        return min(1.0, max(0.0, quality_score))
    
    def _calculate_freshness_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate freshness score based on timestamps"""
        timestamp = metadata.get('modified_at') or metadata.get('created_at')
        if not timestamp:
            return 0.5 
        
        try:
            date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            days_ago = (datetime.now() - date).days
            
            if days_ago < 30:
                return self.quality_indicators['freshness']['recent']
            elif days_ago < 90:
                return self.quality_indicators['freshness']['moderate']
            elif days_ago < 180:
                return self.quality_indicators['freshness']['stale']
            else:
                return self.quality_indicators['freshness']['very_stale']
        except:
            return 0.5
    
    def _calculate_cross_reference_score(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> float:
        """Calculate how well this document is cross-referenced"""
        terms = self._extract_terms(doc.get('content', ''))
        
        if not terms:
            return 0.3
        
        reference_count = 0
        for term in terms:
            if term in integration_map['term_index']:
                
                other_refs = [ref for ref in integration_map['term_index'][term] 
                             if not ref.startswith(source_type + ':')]
                reference_count += len(other_refs)
        
        
        avg_references = reference_count / len(terms) if terms else 0
        
      
        if avg_references >= 3:
            return 1.0
        elif avg_references >= 1:
            return 0.8
        elif avg_references >= 0.5:
            return 0.6
        else:
            return 0.3
    
    def _calculate_completeness_score(self, doc: Dict[str, Any], source_type: str) -> float:
        """Calculate completeness score based on content quality"""
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        
        score = 0.5  
        
        
        if source_type == 'code':
            if metadata.get('docstring'):
                score += 0.2
            if metadata.get('arguments'):
                score += 0.1
            if len(content) > 50:
                score += 0.2
        
        elif source_type == 'documents':
            if metadata.get('structure', {}).get('has_headers'):
                score += 0.2
            if metadata.get('structure', {}).get('has_code_blocks'):
                score += 0.1
            if len(content.split()) > 100:
                score += 0.2
        
        elif source_type in ['pull_requests', 'tickets']:
            if len(content) > 100:
                score += 0.2
            if metadata.get('status'):
                score += 0.1
            if metadata.get('labels') or metadata.get('tags'):
                score += 0.2
        
        return min(1.0, score)
    
    def _calculate_consistency_score(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> float:
        """Calculate consistency with related content"""
        
        content = doc.get('content', '').lower()
        
        
        inconsistency_indicators = 0
        
      
        for pattern in self.issue_patterns.values():
            if re.search(pattern, content, re.IGNORECASE):
                inconsistency_indicators += 1
        
        
        terms = self._extract_terms(content)
        version_conflicts = 0
        
        for term in terms:
            if term in integration_map['term_index']:
                related_docs = integration_map['term_index'][term]
                for related_id in related_docs:
                    if related_id in integration_map['content_index']:
                        related_content = integration_map['content_index'][related_id]['content']
                        if re.search(self.issue_patterns['version_mismatch'], related_content, re.IGNORECASE):
                            version_conflicts += 1
        
        
        if inconsistency_indicators == 0 and version_conflicts == 0:
            return self.quality_indicators['consistency']['consistent']
        elif inconsistency_indicators <= 1 and version_conflicts <= 1:
            return self.quality_indicators['consistency']['minor_issues']
        elif inconsistency_indicators <= 3 and version_conflicts <= 2:
            return self.quality_indicators['consistency']['major_issues']
        else:
            return self.quality_indicators['consistency']['inconsistent']
    
    def _find_relationships(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> List[Dict[str, Any]]:
        """Find relationships between this document and others"""
        relationships = []
        content = doc.get('content', '').lower()
        
        
        for rel_type, rel_config in self.relationship_patterns.items():
            for pattern in rel_config['patterns']:
                if re.search(pattern, content, re.IGNORECASE):
                    
                    related_docs = self._find_related_documents(doc, integration_map, source_type, rel_type)
                    for related_doc in related_docs:
                        relationships.append({
                            'type': rel_type,
                            'target': related_doc,
                            'confidence': rel_config['strength'],
                            'evidence': pattern
                        })
        
        return relationships[:10]  
    
    def _find_related_documents(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str, rel_type: str) -> List[str]:
        """Find documents related to this one"""
        related_docs = []
        terms = self._extract_terms(doc.get('content', ''))
        
        
        term_matches = {}
        for term in terms:
            if term in integration_map['term_index']:
                for related_id in integration_map['term_index'][term]:
                    if related_id != self._generate_doc_id(doc, source_type):
                        term_matches[related_id] = term_matches.get(related_id, 0) + 1
        
        
        sorted_matches = sorted(term_matches.items(), key=lambda x: x[1], reverse=True)
        
        
        return [doc_id for doc_id, count in sorted_matches[:5] if count >= 2]
    
    def _detect_integration_issues(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> List[Dict[str, Any]]:
        """Detect integration issues"""
        issues = []
        content = doc.get('content', '').lower()
        metadata = doc.get('metadata', {})
        
        
        for issue_type, pattern in self.issue_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    'type': issue_type,
                    'severity': self._assess_issue_severity(issue_type, content),
                    'description': self._get_issue_description(issue_type),
                    'suggestion': self._get_issue_suggestion(issue_type, source_type)
                })
        
        
        source_issues = self._detect_source_specific_issues(doc, integration_map, source_type)
        issues.extend(source_issues)
        
        return issues
    
    def _assess_issue_severity(self, issue_type: str, content: str) -> str:
        """Assess the severity of an issue"""
        severity_map = {
            'stale_content': 'medium',
            'missing_documentation': 'high',
            'broken_links': 'high',
            'version_mismatch': 'high',
            'incomplete_implementation': 'medium'
        }
        return severity_map.get(issue_type, 'low')
    
    def _get_issue_description(self, issue_type: str) -> str:
        """Get human-readable description of the issue"""
        descriptions = {
            'stale_content': 'Content contains stale or temporary markers',
            'missing_documentation': 'Documentation is missing or incomplete',
            'broken_links': 'Contains broken or invalid links',
            'version_mismatch': 'Version inconsistencies detected',
            'incomplete_implementation': 'Implementation appears incomplete'
        }
        return descriptions.get(issue_type, 'Unknown issue detected')
    
    def _get_issue_suggestion(self, issue_type: str, source_type: str) -> str:
        """Get suggestion for fixing the issue"""
        suggestions = {
            'stale_content': 'Review and update temporary markers and TODOs',
            'missing_documentation': 'Add comprehensive documentation',
            'broken_links': 'Verify and fix broken links',
            'version_mismatch': 'Ensure version consistency across sources',
            'incomplete_implementation': 'Complete the implementation or mark as work in progress'
        }
        return suggestions.get(issue_type, 'Review and address the issue')
    
    def _detect_source_specific_issues(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> List[Dict[str, Any]]:
        """Detect issues specific to the source type"""
        issues = []
        metadata = doc.get('metadata', {})
        
        if source_type == 'code':
            
            if not metadata.get('docstring') and metadata.get('structure_type') == 'function':
                issues.append({
                    'type': 'missing_docstring',
                    'severity': 'medium',
                    'description': 'Function lacks documentation',
                    'suggestion': 'Add docstring to explain function purpose and parameters'
                })
        
        elif source_type == 'documents':
            
            if len(doc.get('content', '')) < 100:
                issues.append({
                    'type': 'insufficient_content',
                    'severity': 'medium',
                    'description': 'Documentation is very brief',
                    'suggestion': 'Expand documentation with more details and examples'
                })
        
        return issues
    
    def _extract_semantic_context(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Extract semantic context for this document"""
        semantic_context = {}
        
       
        for context_type, extractor_func in self.semantic_extractors.items():
            if source_type in context_type or 'all' in context_type:
                try:
                    context = extractor_func(doc, integration_map, source_type)
                    if context:
                        semantic_context[context_type] = context
                except Exception as e:
                    logger.debug(f"Error extracting {context_type} context: {e}")
        
        return semantic_context
    
    def _extract_code_doc_context(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Extract context between code and documentation"""
        if source_type not in ['code', 'documents']:
            return {}
        
        context = {'linked_items': [], 'coverage': 0.0}
        content = doc.get('content', '').lower()
        metadata = doc.get('metadata', {})
        
        
        code_references = re.findall(r'`([^`]+)`|def\s+(\w+)|class\s+(\w+)', content)
        flattened_refs = [ref for ref_tuple in code_references for ref in ref_tuple if ref]
        
        for ref in flattened_refs:
            if ref in integration_map['term_index']:
                related_docs = integration_map['term_index'][ref]
                for related_id in related_docs:
                    if related_id in integration_map['content_index']:
                        related_info = integration_map['content_index'][related_id]
                        if (source_type == 'code' and related_info['source'] == 'documents') or \
                           (source_type == 'documents' and related_info['source'] == 'code'):
                            context['linked_items'].append({
                                'reference': ref,
                                'target': related_id,
                                'target_type': related_info['source']
                            })
        
        
        if flattened_refs:
            context['coverage'] = len(context['linked_items']) / len(flattened_refs)
        
        return context
    
    def _extract_test_code_context(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Extract context between tests and code"""
        if source_type != 'code':
            return {}
        
        context = {'tested_functions': [], 'coverage': 0.0}
        content = doc.get('content', '').lower()
        metadata = doc.get('metadata', {})
        
        
        is_test = ('test' in metadata.get('file_path', '').lower() or 
                  'test' in metadata.get('name', '').lower() or
                  'test_' in content)
        
        if is_test:
            
            test_calls = re.findall(r'(\w+)\s*\(', content)
            for call in test_calls:
                if call in integration_map['term_index']:
                    related_docs = integration_map['term_index'][call]
                    for related_id in related_docs:
                        if related_id in integration_map['content_index']:
                            related_info = integration_map['content_index'][related_id]
                            if (related_info['source'] == 'code' and 
                                'test' not in related_id.lower()):
                                context['tested_functions'].append({
                                    'function': call,
                                    'target': related_id
                                })
        
        context['coverage'] = min(1.0, len(context['tested_functions']) / 10)  
        return context
    
    def _extract_ticket_code_context(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Extract context between tickets and code"""
        if source_type != 'tickets':
            return {}
        
        context = {'referenced_files': [], 'implementation_status': 'unknown'}
        content = doc.get('content', '').lower()
        
        
        file_refs = re.findall(r'(\w+\.\w+|/[\w/]+\.[\w]+)', content)
        for file_ref in file_refs:
            if file_ref in integration_map['file_index']:
                related_docs = integration_map['file_index'][file_ref]
                context['referenced_files'].extend([{
                    'file': file_ref,
                    'related_docs': related_docs
                }])
        
        
        if re.search(r'implemented|completed|done|closed', content):
            context['implementation_status'] = 'completed'
        elif re.search(r'in\s+progress|working|developing', content):
            context['implementation_status'] = 'in_progress'
        elif re.search(r'todo|planned|backlog', content):
            context['implementation_status'] = 'planned'
        
        return context
    
    def _extract_pr_code_context(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Extract context between pull requests and code"""
        if source_type != 'pull_requests':
            return {}
        
        context = {'modified_files': [], 'impact_scope': 'unknown'}
        content = doc.get('content', '').lower()
        metadata = doc.get('metadata', {})
        
        
        file_refs = re.findall(r'(\w+\.\w+|/[\w/]+\.[\w]+)', content)
        for file_ref in file_refs:
            if file_ref in integration_map['file_index']:
                related_docs = integration_map['file_index'][file_ref]
                context['modified_files'].append({
                    'file': file_ref,
                    'related_docs': related_docs
                })
        
      
        if len(context['modified_files']) > 10:
            context['impact_scope'] = 'major'
        elif len(context['modified_files']) > 3:
            context['impact_scope'] = 'moderate'
        else:
            context['impact_scope'] = 'minor'
        
        return context
    
    def _extract_conversation_context(self, doc: Dict[str, Any], integration_map: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Extract context from conversations to all other sources"""
        if source_type != 'conversations':
            return {}
        
        context = {'discussed_topics': [], 'mentioned_files': [], 'action_items': []}
        content = doc.get('content', '').lower()
        
        
        technical_terms = re.findall(r'\b(api|function|class|bug|feature|deploy|test|build)\w*\b', content)
        for term in technical_terms:
            if term in integration_map['term_index']:
                related_docs = integration_map['term_index'][term]
                context['discussed_topics'].append({
                    'topic': term,
                    'related_docs': related_docs[:3]  # Limit to top 3
                })
        
        file_refs = re.findall(r'(\w+\.\w+|/[\w/]+\.[\w]+)', content)
        for file_ref in file_refs:
            if file_ref in integration_map['file_index']:
                context['mentioned_files'].append({
                    'file': file_ref,
                    'related_docs': integration_map['file_index'][file_ref]
                })
        
        
        action_patterns = [
            r'need\s+to\s+(\w+)', r'should\s+(\w+)', r'will\s+(\w+)', 
            r'todo:?\s*(\w+)', r'action:?\s*(\w+)'
        ]
        for pattern in action_patterns:
            actions = re.findall(pattern, content)
            context['action_items'].extend(actions)
        
        return context
    
    def _create_integration_summary(self, doc: Dict[str, Any], integration_analysis: Dict[str, Any], source_type: str) -> str:
        """Create LLM-friendly summary of integration analysis"""
        quality_score = integration_analysis.get('quality_score', 0.0)
        relationships = integration_analysis.get('relationships', [])
        issues = integration_analysis.get('issues', [])
        
        
        summary_parts = []
        
        
        if quality_score >= 0.8:
            quality_desc = "high-quality"
        elif quality_score >= 0.6:
            quality_desc = "good-quality"
        elif quality_score >= 0.4:
            quality_desc = "moderate-quality"
        else:
            quality_desc = "needs-improvement"
        
        summary_parts.append(f"This is a {quality_desc} {source_type} document")
        
        
        if relationships:
            rel_types = list(set(rel['type'] for rel in relationships))
            summary_parts.append(f"with {len(relationships)} relationships ({', '.join(rel_types)})")
        
       
        if issues:
            high_severity_issues = [i for i in issues if i.get('severity') == 'high']
            if high_severity_issues:
                summary_parts.append(f"and {len(high_severity_issues)} high-priority integration issues")
            else:
                summary_parts.append(f"and {len(issues)} minor integration issues")
        
        
        summary_parts.append(f"Integration quality score: {quality_score:.2f}")
        
        return '. '.join(summary_parts) + '.'
    
    def _create_global_integration_summary(self, results: Dict[str, List[Dict[str, Any]]], integration_map: Dict[str, Any]) -> Dict[str, Any]:
        """Create global integration summary across all sources"""
        summary = {
            'total_documents': sum(len(docs) for docs in results.values()),
            'source_counts': {source: len(docs) for source, docs in results.items()},
            'integration_quality': {},
            'cross_references': 0,
            'common_issues': {},
            'relationship_distribution': {},
            'recommendations': []
        }
        
      
        for source_type, documents in results.items():
            if documents:
                quality_scores = [doc.get('metadata', {}).get('integration', {}).get('quality_score', 0.0) 
                                for doc in documents]
                summary['integration_quality'][source_type] = {
                    'average': sum(quality_scores) / len(quality_scores),
                    'min': min(quality_scores),
                    'max': max(quality_scores)
                }
        
       
        summary['cross_references'] = len(integration_map['term_index'])
        
      
        all_issues = []
        for source_type, documents in results.items():
            for doc in documents:
                doc_issues = doc.get('metadata', {}).get('integration', {}).get('issues', [])
                all_issues.extend(doc_issues)
        
        issue_counts = {}
        for issue in all_issues:
            issue_type = issue.get('type', 'unknown')
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        summary['common_issues'] = issue_counts
        
       
        all_relationships = []
        for source_type, documents in results.items():
            for doc in documents:
                doc_relationships = doc.get('metadata', {}).get('integration', {}).get('relationships', [])
                all_relationships.extend(doc_relationships)
        
        rel_counts = {}
        for rel in all_relationships:
            rel_type = rel.get('type', 'unknown')
            rel_counts[rel_type] = rel_counts.get(rel_type, 0) + 1
        
        summary['relationship_distribution'] = rel_counts
        
       
        recommendations = []
        
        
        for source_type, quality_info in summary['integration_quality'].items():
            if quality_info['average'] < 0.6:
                recommendations.append(f"Improve {source_type} integration quality (current: {quality_info['average']:.2f})")
        
      
        for issue_type, count in issue_counts.items():
            if count > len(summary['total_documents']) * 0.1:  
                recommendations.append(f"Address widespread {issue_type} issues ({count} occurrences)")
        
        
        if rel_counts.get('references', 0) < summary['total_documents'] * 0.3:
            recommendations.append("Increase cross-referencing between sources")
        
        summary['recommendations'] = recommendations
        
        return summary

    async def ingest_single_source(self, source_type: str, **kwargs) -> List[Dict[str, Any]]:
        scenario = kwargs.get('scenario', self.scenario or 'startup')
        
        if source_type == 'code':
            return await self.code_parser.parse_codebase(
                base_path=kwargs.get('base_path'),
                scenario=scenario if self.demo_mode else None
            )
        
        elif source_type == 'documents':
            return await self.doc_ingestor.ingest_docs(
                base_path=kwargs.get('base_path'),
                scenario=scenario if self.demo_mode else None
            )
        
        elif source_type == 'pull_requests':
            return await self.pr_fetcher.fetch_pull_requests(
                repo_url=kwargs.get('repo_url'),
                limit=kwargs.get('limit', 20),
                scenario=scenario if self.demo_mode else None
            )
        
        elif source_type == 'conversations':
            return await self.slack_parser.parse_slack_export(
                export_path=kwargs.get('export_path'),
                scenario=scenario if self.demo_mode else None
            )
        
        elif source_type == 'tickets':
            return await self.ticket_fetcher.fetch_tickets(
                source=kwargs.get('source', 'mock'),
                limit=kwargs.get('limit', 20),
                scenario=scenario if self.demo_mode else None
            )
        
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    def get_available_sources(self) -> List[str]:
        return ['code', 'documents', 'pull_requests', 'conversations', 'tickets']
    
    def get_available_scenarios(self) -> List[str]:
        return ['startup', 'enterprise', 'freelancer']
    
    def get_source_status(self) -> Dict[str, Dict[str, Any]]:
        status = {}
        
        for source in self.get_available_sources():
            if source == 'code':
                component = self.code_parser
            elif source == 'documents':
                component = self.doc_ingestor
            elif source == 'pull_requests':
                component = self.pr_fetcher
            elif source == 'conversations':
                component = self.slack_parser
            elif source == 'tickets':
                component = self.ticket_fetcher
            
            if hasattr(component, 'get_parsing_stats'):
                status[source] = component.get_parsing_stats()
            elif hasattr(component, 'get_ingestion_stats'):
                status[source] = component.get_ingestion_stats()
            elif hasattr(component, 'get_fetch_stats'):
                status[source] = component.get_fetch_stats()
            elif hasattr(component, 'get_fetcher_stats'):
                status[source] = component.get_fetcher_stats()
            else:
                status[source] = {
                    'demo_mode': self.demo_mode,
                    'user_id': self.user_id,
                    'available': True
                }
        
        return status
    
    def validate_configuration(self) -> Dict[str, Any]:
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'demo_mode': self.demo_mode,
            'user_id': self.user_id
        }
        
        if not self.demo_mode:
            config_paths = {
                'code': self.config.get('data_sources', {}).get('codebase', {}).get('path'),
                'documents': self.config.get('data_sources', {}).get('documentation', {}).get('path'),
                'github_repo': self.config.get('data_sources', {}).get('github', {}).get('repo_url'),
                'slack_export': self.config.get('data_sources', {}).get('slack_export', {}).get('path')
            }
            
            for source, path in config_paths.items():
                if not path:
                    validation_results['warnings'].append(f"No configuration found for {source}")
                elif source in ['code', 'documents', 'slack_export'] and not os.path.exists(path):
                    validation_results['errors'].append(f"Path does not exist for {source}: {path}")
            
            env_vars = {
                'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
                'JIRA_API_TOKEN': os.getenv('JIRA_API_TOKEN'),
                'JIRA_EMAIL': os.getenv('JIRA_EMAIL'),
                'JIRA_URL': os.getenv('JIRA_URL')
            }
            
            for var, value in env_vars.items():
                if not value:
                    validation_results['warnings'].append(f"Environment variable not set: {var}")
        
        if validation_results['errors']:
            validation_results['valid'] = False
        
        return validation_results
    
    async def test_all_sources(self, scenario: str = None) -> Dict[str, Any]:
        scenario = scenario or 'startup'
        test_results = {}
        
        for source in self.get_available_sources():
            try:
                start_time = datetime.now()
                
                if source == 'code':
                    documents = await self.code_parser.parse_codebase(scenario=scenario if self.demo_mode else None)
                elif source == 'documents':
                    documents = await self.doc_ingestor.ingest_docs(scenario=scenario if self.demo_mode else None)
                elif source == 'pull_requests':
                    documents = await self.pr_fetcher.fetch_pull_requests(limit=5, scenario=scenario if self.demo_mode else None)
                elif source == 'conversations':
                    documents = await self.slack_parser.parse_slack_export(scenario=scenario if self.demo_mode else None)
                elif source == 'tickets':
                    documents = await self.ticket_fetcher.fetch_tickets(limit=5, scenario=scenario if self.demo_mode else None)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                test_results[source] = {
                    'success': True,
                    'document_count': len(documents),
                    'duration_seconds': duration,
                    'error': None,
                    
                    'integration_quality': self._calculate_test_integration_quality(documents),
                    'cross_references': self._count_test_cross_references(documents),
                    'detected_issues': self._count_test_issues(documents)
                }
                
            except Exception as e:
                test_results[source] = {
                    'success': False,
                    'document_count': 0,
                    'duration_seconds': 0,
                    'error': str(e),
                    'integration_quality': 0.0,
                    'cross_references': 0,
                    'detected_issues': 0
                }
        
        return test_results
    
    def _calculate_test_integration_quality(self, documents: List[Dict[str, Any]]) -> float:
        """Calculate average integration quality for test results"""
        if not documents:
            return 0.0
        
        quality_scores = []
        for doc in documents:
            integration = doc.get('metadata', {}).get('integration', {})
            quality_scores.append(integration.get('quality_score', 0.0))
        
        return sum(quality_scores) / len(quality_scores)
    
    def _count_test_cross_references(self, documents: List[Dict[str, Any]]) -> int:
        """Count cross-references in test results"""
        cross_ref_count = 0
        for doc in documents:
            integration = doc.get('metadata', {}).get('integration', {})
            relationships = integration.get('relationships', [])
            cross_ref_count += len(relationships)
        
        return cross_ref_count
    
    def _count_test_issues(self, documents: List[Dict[str, Any]]) -> int:
        """Count issues in test results"""
        issue_count = 0
        for doc in documents:
            integration = doc.get('metadata', {}).get('integration', {})
            issues = integration.get('issues', [])
            issue_count += len(issues)
        
        return issue_count
    
    def get_integration_stats(self) -> Dict[str, Any]:
        return {
            'demo_mode': self.demo_mode,
            'user_id': self.user_id,
            'scenario': self.scenario,
            'available_sources': self.get_available_sources(),
            'available_scenarios': self.get_available_scenarios(),
            'components_initialized': {
                'code_parser': hasattr(self, 'code_parser'),
                'doc_ingestor': hasattr(self, 'doc_ingestor'),
                'pr_fetcher': hasattr(self, 'pr_fetcher'),
                'slack_parser': hasattr(self, 'slack_parser'),
                'ticket_fetcher': hasattr(self, 'ticket_fetcher'),
                'synthetic_generator': hasattr(self, 'synthetic_generator'),
                'demo_github': hasattr(self, 'demo_github'),
                'demo_slack': hasattr(self, 'demo_slack'),
                'demo_jira': hasattr(self, 'demo_jira')
            },
            'enhanced_features': {
                'integration_quality_scoring': True,
                'relationship_inference': True,
                'issue_detection': True,
                'semantic_context_extraction': True,
                'cross_reference_analysis': True,
                'llm_friendly_summaries': True
            }
        }


async def ingest_all_quick(demo_mode: bool = False, scenario: str = 'startup', user_id: str = None) -> Dict[str, List[Dict[str, Any]]]:
    manager = IntegrationManager(demo_mode=demo_mode, user_id=user_id)
    return await manager.ingest_all_data_sources(scenario)

if __name__ == "__main__":
    import sys
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
            
            manager = IntegrationManager(demo_mode=demo_mode, user_id=user_id)
            
            if command == "ingest":
                scenario = scenario or 'startup'
                results = await manager.ingest_all_data_sources(scenario)
                
                total_docs = sum(len(docs) for docs in results.values() if isinstance(docs, list))
                print(f"Ingested {total_docs} total documents with enhanced integration analysis")
                
                for source, docs in results.items():
                    if isinstance(docs, list):
                        print(f"  {source}: {len(docs)} documents")
                        
                       
                        if docs:
                            avg_quality = sum(doc.get('metadata', {}).get('integration', {}).get('quality_score', 0.0) 
                                            for doc in docs) / len(docs)
                            total_relationships = sum(len(doc.get('metadata', {}).get('integration', {}).get('relationships', [])) 
                                                    for doc in docs)
                            total_issues = sum(len(doc.get('metadata', {}).get('integration', {}).get('issues', [])) 
                                             for doc in docs)
                            
                            print(f"    Integration Quality: {avg_quality:.2f}")
                            print(f"    Cross-references: {total_relationships}")
                            print(f"    Issues detected: {total_issues}")
                    
                
                if '_integration_summary' in results:
                    global_summary = results['_integration_summary']
                    print(f"\nGlobal Integration Summary:")
                    print(f"  Total cross-references: {global_summary['cross_references']}")
                    print(f"  Common issues: {list(global_summary['common_issues'].keys())}")
                    if global_summary['recommendations']:
                        print(f"  Recommendations: {len(global_summary['recommendations'])}")
                        for rec in global_summary['recommendations'][:3]:
                            print(f"    - {rec}")
                    
            elif command == "test":
                scenario = scenario or 'startup'
                results = await manager.test_all_sources(scenario)
                
                print("Enhanced source testing results:")
                for source, result in results.items():
                    status = " PASS" if result['success'] else " FAIL"
                    print(f"  {source}: {status}")
                    print(f"    Documents: {result['document_count']}")
                    print(f"    Duration: {result['duration_seconds']:.2f}s")
                    print(f"    Integration Quality: {result['integration_quality']:.2f}")
                    print(f"    Cross-references: {result['cross_references']}")
                    print(f"    Issues: {result['detected_issues']}")
                    if result['error']:
                        print(f"    Error: {result['error']}")
                        
            elif command == "validate":
                validation = manager.validate_configuration()
                print("Configuration Validation:")
                print(f"  Valid: {validation['valid']}")
                if validation['warnings']:
                    print("  Warnings:")
                    for warning in validation['warnings']:
                        print(f"    - {warning}")
                if validation['errors']:
                    print("  Errors:")
                    for error in validation['errors']:
                        print(f"    - {error}")
                        
            elif command == "status":
                status = manager.get_source_status()
                print("Source Status:")
                print(json.dumps(status, indent=2))
                
            elif command == "stats":
                stats = manager.get_integration_stats()
                print("Enhanced Integration Manager Statistics:")
                print(json.dumps(stats, indent=2))
                
            elif command == "sources":
                sources = manager.get_available_sources()
                scenarios = manager.get_available_scenarios()
                print("Available Sources:")
                for source in sources:
                    print(f"  - {source}")
                print("Available Scenarios:")
                for scenario in scenarios:
                    print(f"  - {scenario}")
                    
            else:
                print("Available commands:")
                print("  ingest [--demo] [--user USER_ID] [--scenario SCENARIO] - Ingest all data sources with integration analysis")
                print("  test [--demo] [--scenario SCENARIO] - Test all data sources with enhanced metrics")
                print("  validate - Validate configuration")
                print("  status - Show source status")
                print("  stats - Show enhanced integration statistics")
                print("  sources - List available sources and scenarios")
        else:
            print("Usage: python integration_manager.py [command] [options]")
            print("Commands: ingest, test, validate, status, stats, sources")
            print("Options:")
            print("  --demo              Enable demo mode")
            print("  --user USER_ID      Set user ID")
            print("  --scenario NAME     Set demo scenario (startup/enterprise/freelancer)")
            print("\nEnhanced Features:")
            print("  ✓ Integration quality scoring")
            print("  ✓ Relationship inference (supports, extends, explains, etc.)")
            print("  ✓ Issue detection (stale content, missing docs, etc.)")
            print("  ✓ Semantic context extraction")
            print("  ✓ Cross-reference analysis")
            print("  ✓ LLM-friendly integration summaries")
    
    asyncio.run(main())