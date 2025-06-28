import os
import ast
import yaml
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from loguru import logger
from datetime import datetime
import hashlib
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, extract_file_metadata, sanitize_text

class CodeParser:
    """
    Code Parser: Extracts and processes code files for indexing
    Handles multiple programming languages with syntax-aware parsing
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.supported_extensions = self._get_supported_extensions()
        self.language_parsers = self._setup_language_parsers()
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_supported_extensions(self) -> Set[str]:
        """Get supported file extensions from config"""
        return set(self.config['data_sources']['codebase']['extensions'])
    
    def _setup_language_parsers(self) -> Dict[str, Any]:
        """Setup language-specific parsers"""
        return {
            '.py': self._parse_python,
            '.js': self._parse_javascript,
            '.ts': self._parse_typescript,
            '.jsx': self._parse_jsx,
            '.tsx': self._parse_tsx,
            '.java': self._parse_java,
            '.go': self._parse_go,
            '.rs': self._parse_rust,
            '.cpp': self._parse_cpp,
            '.c': self._parse_c,
            '.h': self._parse_header
        }
    
    async def parse_codebase(self, base_path: str = None) -> List[Dict[str, Any]]:
        """
        Parse entire codebase and extract structured information
        
        Args:
            base_path: Root path to parse (defaults to config path)
            
        Returns:
            List of document dictionaries ready for indexing
        """
        if not base_path:
            base_path = self.config['data_sources']['codebase']['path']
        
        base_path = Path(base_path).resolve()
        
        if not base_path.exists():
            logger.warning(f"Codebase path does not exist: {base_path}")
            return []
        
        logger.info(f"Starting codebase parsing from: {base_path}")
        
        documents = []
        ignore_patterns = self.config['data_sources']['codebase']['ignore_patterns']
        
      
        for file_path in self._walk_directory(base_path, ignore_patterns):
            try:
                if file_path.suffix in self.supported_extensions:
                    file_documents = await self._parse_file(file_path, base_path)
                    documents.extend(file_documents)
                    
            except Exception as e:
                logger.error(f"Error parsing file {file_path}: {str(e)}")
                continue
        
        logger.info(f"Parsed {len(documents)} code documents from {base_path}")
        return documents
    
    def _walk_directory(self, base_path: Path, ignore_patterns: List[str]) -> List[Path]:
        """Walk directory and yield relevant files"""
        files = []
        
        for root, dirs, filenames in os.walk(base_path):
           
            dirs[:] = [d for d in dirs if not self._should_ignore(d, ignore_patterns)]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
              
                if self._should_ignore(str(file_path), ignore_patterns):
                    continue
                
               
                if file_path.suffix in self.supported_extensions:
                    files.append(file_path)
        
        return files
    
    def _should_ignore(self, path: str, ignore_patterns: List[str]) -> bool:
        """Check if path should be ignored based on patterns"""
        path_str = str(path).lower()
        
        for pattern in ignore_patterns:
            if pattern.lower() in path_str:
                return True
        
        return False
    
    async def _parse_file(self, file_path: Path, base_path: Path) -> List[Dict[str, Any]]:
        """Parse a single file and extract code structures"""
        try:
           
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return []
            
           
            relative_path = file_path.relative_to(base_path)
            
          
            file_metadata = extract_file_metadata(file_path)
            
          
            extension = file_path.suffix
            parser_func = self.language_parsers.get(extension, self._parse_generic)
            
            parsed_structures = parser_func(content, str(relative_path))
            
          
            documents = []
            for structure in parsed_structures:
                doc = {
                    'content': structure['content'],
                    'metadata': {
                        'source_type': 'code',
                        'file_path': str(relative_path),
                        'language': self._get_language_from_extension(extension),
                        'structure_type': structure['type'],
                        'name': structure.get('name', ''),
                        'line_start': structure.get('line_start', 1),
                        'line_end': structure.get('line_end', 1),
                        'file_size': file_metadata['size'],
                        'created_at': file_metadata['created_at'],
                        'modified_at': file_metadata['modified_at'],
                        'content_hash': get_file_hash(content),
                        'tags': structure.get('tags', []),
                        'complexity': structure.get('complexity', 'medium'),
                        'dependencies': structure.get('dependencies', [])
                    }
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            return []
    
    def _get_language_from_extension(self, extension: str) -> str:
        """Map file extension to language name"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c'
        }
        return language_map.get(extension, 'unknown')
    
    def _parse_python(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse Python files using AST"""
        structures = []
        
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_python_function(node, lines, file_path)
                    structures.append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_python_class(node, lines, file_path)
                    structures.append(class_info)
            
         
            module_info = {
                'type': 'module',
                'name': Path(file_path).stem,
                'content': content,
                'line_start': 1,
                'line_end': len(lines),
                'tags': self._extract_python_imports(tree),
                'complexity': self._estimate_complexity(content)
            }
            structures.append(module_info)
            
        except SyntaxError as e:
            logger.warning(f"Syntax error in Python file {file_path}: {str(e)}")
           
            structures = self._parse_generic(content, file_path)
        
        return structures
    
    def _extract_python_function(self, node: ast.FunctionDef, lines: List[str], file_path: str) -> Dict[str, Any]:
        """Extract Python function information"""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
       
        func_lines = lines[start_line-1:end_line]
        func_content = '\n'.join(func_lines)
        
      
        docstring = ast.get_docstring(node) or ""
        
      
        args = [arg.arg for arg in node.args.args]
        
        return {
            'type': 'function',
            'name': node.name,
            'content': func_content,
            'line_start': start_line,
            'line_end': end_line,
            'tags': ['function', node.name] + args,
            'complexity': self._estimate_function_complexity(node),
            'docstring': docstring,
            'arguments': args,
            'is_async': isinstance(node, ast.AsyncFunctionDef)
        }
    
    def _extract_python_class(self, node: ast.ClassDef, lines: List[str], file_path: str) -> Dict[str, Any]:
        """Extract Python class information"""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
       
        class_lines = lines[start_line-1:end_line]
        class_content = '\n'.join(class_lines)
        
        
        docstring = ast.get_docstring(node) or ""
        
     
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        
        return {
            'type': 'class',
            'name': node.name,
            'content': class_content,
            'line_start': start_line,
            'line_end': end_line,
            'tags': ['class', node.name] + methods,
            'complexity': self._estimate_class_complexity(node),
            'docstring': docstring,
            'methods': methods,
            'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)]
        }
    
    def _extract_python_imports(self, tree: ast.AST) -> List[str]:
        """Extract import information from Python AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    
    def _parse_javascript(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse JavaScript files"""
        return self._parse_generic_with_patterns(
            content, file_path, 'javascript',
            function_patterns=[r'function\s+(\w+)', r'(\w+)\s*:\s*function', r'const\s+(\w+)\s*=.*=>'],
            class_patterns=[r'class\s+(\w+)']
        )
    
    def _parse_typescript(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse TypeScript files"""
        return self._parse_generic_with_patterns(
            content, file_path, 'typescript',
            function_patterns=[r'function\s+(\w+)', r'(\w+)\s*:\s*function', r'const\s+(\w+)\s*=.*=>', r'(\w+)\s*\([^)]*\)\s*:\s*\w+'],
            class_patterns=[r'class\s+(\w+)', r'interface\s+(\w+)', r'type\s+(\w+)']
        )
    
    def _parse_jsx(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse JSX files"""
        structures = self._parse_javascript(content, file_path)
        
       
        for structure in structures:
            structure['tags'].extend(['react', 'jsx'])
            
        return structures
    
    def _parse_tsx(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse TSX files"""
        structures = self._parse_typescript(content, file_path)
        
       
        for structure in structures:
            structure['tags'].extend(['react', 'tsx'])
            
        return structures
    
    def _parse_java(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse Java files"""
        return self._parse_generic_with_patterns(
            content, file_path, 'java',
            function_patterns=[r'(public|private|protected)?\s*\w+\s+(\w+)\s*\('],
            class_patterns=[r'(public|private)?\s*class\s+(\w+)', r'interface\s+(\w+)']
        )
    
    def _parse_go(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse Go files"""
        return self._parse_generic_with_patterns(
            content, file_path, 'go',
            function_patterns=[r'func\s+(\w+)', r'func\s+\(\w+\s+\*?\w+\)\s+(\w+)'],
            class_patterns=[r'type\s+(\w+)\s+struct']
        )
    
    def _parse_rust(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse Rust files"""
        return self._parse_generic_with_patterns(
            content, file_path, 'rust',
            function_patterns=[r'fn\s+(\w+)', r'pub\s+fn\s+(\w+)'],
            class_patterns=[r'struct\s+(\w+)', r'enum\s+(\w+)', r'trait\s+(\w+)']
        )
    
    def _parse_cpp(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse C++ files"""
        return self._parse_generic_with_patterns(
            content, file_path, 'cpp',
            function_patterns=[r'\w+\s+(\w+)\s*\(', r'(\w+)::\w+\s*\('],
            class_patterns=[r'class\s+(\w+)', r'struct\s+(\w+)']
        )
    
    def _parse_c(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse C files"""
        return self._parse_generic_with_patterns(
            content, file_path, 'c',
            function_patterns=[r'\w+\s+(\w+)\s*\('],
            class_patterns=[r'struct\s+(\w+)', r'typedef\s+struct.*?(\w+)']
        )
    
    def _parse_header(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse header files (.h)"""
        return self._parse_generic_with_patterns(
            content, file_path, 'c',
            function_patterns=[r'\w+\s+(\w+)\s*\('],
            class_patterns=[r'struct\s+(\w+)', r'typedef\s+struct.*?(\w+)']
        )
    
    def _parse_generic_with_patterns(
        self, 
        content: str, 
        file_path: str, 
        language: str,
        function_patterns: List[str] = None,
        class_patterns: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Generic parsing using regex patterns"""
        import re
        
        structures = []
        lines = content.split('\n')
        
      
        if function_patterns:
            for pattern in function_patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    func_name = match.group(1) if match.groups() else 'unknown'
                    line_num = content[:match.start()].count('\n') + 1
                    
                    structures.append({
                        'type': 'function',
                        'name': func_name,
                        'content': self._extract_block_content(lines, line_num),
                        'line_start': line_num,
                        'line_end': line_num + 10,
                        'tags': ['function', func_name],
                        'complexity': 'medium'
                    })
        
      
        if class_patterns:
            for pattern in class_patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    class_name = match.group(1) if match.groups() else match.group(2) if len(match.groups()) > 1 else 'unknown'
                    line_num = content[:match.start()].count('\n') + 1
                    
                    structures.append({
                        'type': 'class',
                        'name': class_name,
                        'content': self._extract_block_content(lines, line_num),
                        'line_start': line_num,
                        'line_end': line_num + 20,  
                        'tags': ['class', class_name],
                        'complexity': 'medium'
                    })
        
        
        structures.append({
            'type': 'file',
            'name': Path(file_path).stem,
            'content': content,
            'line_start': 1,
            'line_end': len(lines),
            'tags': [language, 'file'],
            'complexity': self._estimate_complexity(content)
        })
        
        return structures
    
    def _parse_generic(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Generic parsing for unsupported file types"""
        lines = content.split('\n')
        
        return [{
            'type': 'file',
            'name': Path(file_path).stem,
            'content': content,
            'line_start': 1,
            'line_end': len(lines),
            'tags': ['file', 'generic'],
            'complexity': self._estimate_complexity(content)
        }]
    
    def _extract_block_content(self, lines: List[str], start_line: int, max_lines: int = 20) -> str:
        """Extract a block of content around a specific line"""
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), start_idx + max_lines)
        return '\n'.join(lines[start_idx:end_idx])
    
    def _estimate_complexity(self, content: str) -> str:
        """Estimate code complexity based on simple metrics"""
        lines = len(content.split('\n'))
        
      
        complexity_indicators = ['if', 'for', 'while', 'try', 'catch', 'switch', 'case']
        indicator_count = sum(content.lower().count(indicator) for indicator in complexity_indicators)
        
        if lines < 20 and indicator_count < 3:
            return 'low'
        elif lines < 100 and indicator_count < 10:
            return 'medium'
        else:
            return 'high'
    
    def _estimate_function_complexity(self, node: ast.FunctionDef) -> str:
        """Estimate Python function complexity"""
       
        nested_count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                nested_count += 1
        
        if nested_count < 3:
            return 'low'
        elif nested_count < 8:
            return 'medium'
        else:
            return 'high'
    
    def _estimate_class_complexity(self, node: ast.ClassDef) -> str:
        """Estimate Python class complexity"""
        method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
        
        if method_count < 5:
            return 'low'
        elif method_count < 15:
            return 'medium'
        else:
            return 'high'


def parse_codebase_quick(base_path: str = None) -> List[Dict[str, Any]]:
    """Quick codebase parsing function"""
    parser = CodeParser()
    import asyncio
    return asyncio.run(parser.parse_codebase(base_path))

if __name__ == "__main__":
   
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            parser = CodeParser()
            
            if command == "parse":
                base_path = sys.argv[2] if len(sys.argv) > 2 else None
                results = await parser.parse_codebase(base_path)
                print(f"Parsed {len(results)} code structures")
                
                
                for i, result in enumerate(results[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"Type: {result['metadata']['structure_type']}")
                    print(f"Name: {result['metadata']['name']}")
                    print(f"File: {result['metadata']['file_path']}")
                    print(f"Content: {result['content'][:100]}...")
                    
            else:
                print("Available commands:")
                print("  parse [path] - Parse codebase from specified path")
        else:
            print("Usage: python code_parser.py [parse] [path]")
    
    asyncio.run(main())