import os
import yaml
import markdown
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from datetime import datetime
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, extract_file_metadata, sanitize_text

class DocIngestor:
    """
    Documentation Ingestor: Processes documentation files for indexing
    Handles Markdown, reStructuredText, and plain text files with structure extraction
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.supported_extensions = {'.md', '.rst', '.txt', '.markdown', '.mkd'}
        self.markdown_parser = markdown.Markdown(extensions=[
            'toc', 'tables', 'fenced_code', 'codehilite'
        ])
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def ingest_docs(self, base_path: str = None) -> List[Dict[str, Any]]:
        """
        Ingest all documentation files from specified path
        
        Args:
            base_path: Root path to search for documentation
            
        Returns:
            List of document dictionaries ready for indexing
        """
        if not base_path:
            base_path = self.config['data_sources']['documentation']['path']
        
        base_path = Path(base_path).resolve()
        
        if not base_path.exists():
            logger.warning(f"Documentation path does not exist: {base_path}")
            return []
        
        logger.info(f"Starting documentation ingestion from: {base_path}")
        
        documents = []
        
        
        for file_path in self._walk_directory(base_path):
            try:
                if file_path.suffix.lower() in self.supported_extensions:
                    file_documents = await self._ingest_file(file_path, base_path)
                    documents.extend(file_documents)
                    
            except Exception as e:
                logger.error(f"Error ingesting file {file_path}: {str(e)}")
                continue
        
        logger.info(f"Ingested {len(documents)} documentation chunks from {base_path}")
        return documents
    
    def _walk_directory(self, base_path: Path) -> List[Path]:
        """Walk directory and collect documentation files"""
        files = []
        
        for root, dirs, filenames in os.walk(base_path):
           
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                if file_path.suffix.lower() in self.supported_extensions:
                    files.append(file_path)
        
        return files
    
    async def _ingest_file(self, file_path: Path, base_path: Path) -> List[Dict[str, Any]]:
        """Ingest a single documentation file"""
        try:
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return []
            
           
            relative_path = file_path.relative_to(base_path)
            
           
            file_metadata = extract_file_metadata(file_path)
            
            
            if file_path.suffix.lower() in {'.md', '.markdown', '.mkd'}:
                documents = self._parse_markdown(content, str(relative_path), file_metadata)
            elif file_path.suffix.lower() == '.rst':
                documents = self._parse_rst(content, str(relative_path), file_metadata)
            else:
                documents = self._parse_text(content, str(relative_path), file_metadata)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {str(e)}")
            return []
    
    def _parse_markdown(self, content: str, file_path: str, file_metadata: Dict) -> List[Dict[str, Any]]:
        """Parse Markdown files and extract structured content"""
        documents = []
        
        
        frontmatter = self._extract_frontmatter(content)
        if frontmatter:
            content = content[frontmatter['end_pos']:]
        
        
        sections = self._split_by_headers(content)
        
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
                    'keywords': self._extract_keywords(clean_content)
                }
            }
            documents.append(doc)
        
        return documents
    
    def _parse_rst(self, content: str, file_path: str, file_metadata: Dict) -> List[Dict[str, Any]]:
        """Parse reStructuredText files"""
       
        sections = self._split_rst_by_headers(content)
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
                    'keywords': self._extract_keywords(clean_content)
                }
            }
            documents.append(doc)
        
        return documents
    
    def _parse_text(self, content: str, file_path: str, file_metadata: Dict) -> List[Dict[str, Any]]:
        """Parse plain text files"""
        
        chunks = self._chunk_text(content)
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
                    'keywords': self._extract_keywords(clean_content)
                }
            }
            documents.append(doc)
        
        return documents
    
    def _extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from markdown"""
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
        """Split markdown content by headers"""
        sections = []
        lines = content.split('\n')
        
        current_section = {
            'title': 'Introduction',
            'level': 0,
            'content': '',
            'start_line': 0
        }
        
        for i, line in enumerate(lines):
            
            header_match = re.match(r'^(#{1,6})\s+(.+), line.strip())
            
            if header_match:
               
                if current_section['content'].strip():
                    sections.append(current_section)
                
               
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
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
        
        return sections
    
    def _split_rst_by_headers(self, content: str) -> List[Dict[str, Any]]:
        """Split RST content by headers"""
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
                
                
                if re.match(r'^[=\-`:\'"~^_*+#<>]{3,}, next_line) and len(next_line) >= len(line.strip()):
                
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
        """Split text into manageable chunks"""
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
        """Extract code blocks from markdown content"""
        code_blocks = []
        

        fenced_pattern = r'```(\w+)?\n(.*?)```'
        for match in re.finditer(fenced_pattern, content, re.DOTALL):
            language = match.group(1) or 'unknown'
            code = match.group(2).strip()
            code_blocks.append({
                'language': language,
                'code': code
            })
        

        indented_pattern = r'\n((?:    .*\n?)+)'
        for match in re.finditer(indented_pattern, content):
            code = match.group(1).strip()

            code = '\n'.join(line[4:] if line.startswith('    ') else line for line in code.split('\n'))
            code_blocks.append({
                'language': 'unknown',
                'code': code
            })
        
        return code_blocks
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract links from markdown content"""
        links = []
        
     
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            links.append({
                'text': text,
                'url': url,
                'type': 'markdown'
            })
        

        ref_pattern = r'\[([^\]]+)\]\[([^\]]+)\]'
        for match in re.finditer(ref_pattern, content):
            text = match.group(1)
            ref = match.group(2)
            links.append({
                'text': text,
                'reference': ref,
                'type': 'reference'
            })
        
        return links
    
    def _extract_tags(self, content: str, frontmatter: Dict = None) -> List[str]:
        """Extract tags and keywords from content"""
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
        """Extract important keywords from content"""
        
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
        """Estimate content difficulty based on various factors"""
        
        
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
        """Ingest a single documentation file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return []
        
        if file_path.suffix.lower() not in self.supported_extensions:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return []
        
        return await self._ingest_file(file_path, file_path.parent)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported documentation formats"""
        return list(self.supported_extensions)
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get statistics about documentation ingestion capabilities"""
        return {
            "supported_extensions": list(self.supported_extensions),
            "markdown_extensions": ['toc', 'tables', 'fenced_code', 'codehilite'],
            "features": [
                "frontmatter_extraction",
                "header_based_sectioning", 
                "code_block_detection",
                "link_extraction",
                "keyword_extraction",
                "difficulty_estimation"
            ]
        }


def ingest_docs_quick(base_path: str = None) -> List[Dict[str, Any]]:
    """Quick documentation ingestion function"""
    ingestor = DocIngestor()
    import asyncio
    return asyncio.run(ingestor.ingest_docs(base_path))

def ingest_single_doc(file_path: str) -> List[Dict[str, Any]]:
    """Quick single file ingestion"""
    ingestor = DocIngestor()
    import asyncio
    return asyncio.run(ingestor.ingest_single_file(file_path))

if __name__ == "__main__":
    
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            ingestor = DocIngestor()
            
            if command == "ingest":
                base_path = sys.argv[2] if len(sys.argv) > 2 else None
                results = await ingestor.ingest_docs(base_path)
                print(f"Ingested {len(results)} documentation chunks")
                
               
                for i, result in enumerate(results[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"Type: {result['metadata']['doc_type']}")
                    print(f"Title: {result['metadata']['section_title']}")
                    print(f"File: {result['metadata']['file_path']}")
                    print(f"Difficulty: {result['metadata']['difficulty']}")
                    print(f"Content: {result['content'][:100]}...")
                    
            elif command == "file":
                if len(sys.argv) < 3:
                    print("Usage: python doc_ingestor.py file <file_path>")
                    return
                    
                file_path = sys.argv[2]
                results = await ingestor.ingest_single_file(file_path)
                print(f"Ingested {len(results)} chunks from {file_path}")
                
                for result in results:
                    print(f"Section: {result['metadata']['section_title']}")
                    print(f"Tags: {result['metadata']['tags']}")
                    print(f"Keywords: {result['metadata']['keywords']}")
                    
            elif command == "stats":
                stats = ingestor.get_ingestion_stats()
                print("Documentation Ingestor Statistics:")
                print(json.dumps(stats, indent=2))
                
            else:
                print("Available commands:")
                print("  ingest [path] - Ingest documentation from specified path")
                print("  file <file_path> - Ingest single documentation file")
                print("  stats - Show ingestor capabilities")
        else:
            print("Usage: python doc_ingestor.py [ingest|file|stats] [args...]")
    
    asyncio.run(main())