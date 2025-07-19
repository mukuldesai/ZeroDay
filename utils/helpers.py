import os
import hashlib
import re
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
import json
from loguru import logger

def get_file_hash(content: str, algorithm: str = 'md5') -> str:
    try:
        if algorithm == 'md5':
            hasher = hashlib.md5()
        elif algorithm == 'sha256':
            hasher = hashlib.sha256()
        elif algorithm == 'sha1':
            hasher = hashlib.sha1()
        else:
            hasher = hashlib.md5()  
        
        hasher.update(content.encode('utf-8'))
        return hasher.hexdigest()
        
    except Exception as e:
        logger.warning(f"Error generating hash: {str(e)}")
        return ""

def extract_file_metadata(file_path: Path) -> Dict[str, Any]:
    try:
        stat = file_path.stat()
        
        return {
            'size': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': file_path.suffix.lower(),
            'name': file_path.name,
            'stem': file_path.stem
        }
        
    except Exception as e:
        logger.warning(f"Error extracting metadata for {file_path}: {str(e)}")
        return {
            'size': 0,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'modified_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extension': file_path.suffix.lower() if file_path.suffix else '',
            'name': file_path.name,
            'stem': file_path.stem
        }

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)  
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)   
    text = re.sub(r'```[\w]*\n', '', text)
    text = re.sub(r'```', '', text)
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\"\'\/]', ' ', text)
    text = ' '.join(text.split())
    
    return text.strip()

def chunk_text_by_sentences(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    if len(text) <= max_chunk_size:
        return [text]
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + " " + sentence
            else:
                current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def extract_technical_terms(text: str) -> List[str]:
    patterns = [
        r'\b[A-Z][a-z]+[A-Z][a-zA-Z]*\b',  
        r'\b[a-z]+_[a-z_]+\b',              
        r'\b[A-Z_]{3,}\b',                  
        r'\b\w+\(\)\b',                     
        r'\b\w+\.\w+\b',                    
    ]
    
    terms = set()
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        terms.update(matches)
    
    stop_words = {'The', 'This', 'That', 'With', 'From', 'For', 'And', 'But', 'Or'}
    terms = {term for term in terms if term not in stop_words and len(term) > 2}
    
    return list(terms)

def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    word_count = len(text.split())
    return max(1, round(word_count / words_per_minute))

def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def validate_file_path(file_path: Union[str, Path]) -> bool:
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False

def safe_json_load(json_str: str) -> Optional[Dict]:
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Invalid JSON: {str(e)}")
        return None

def extract_urls(text: str) -> List[str]:
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    return re.findall(url_pattern, text)

def clean_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\.{2,}', '.', filename)
    filename = re.sub(r'\s+', '_', filename)
    
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename.strip('._')

def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    for d in dicts:
        if not isinstance(d, dict):
            continue
            
        for key, value in d.items():
            if key in result:
                if isinstance(result[key], list) and isinstance(value, list):
                    result[key] = list(set(result[key] + value))  
                elif isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dictionaries(result[key], value)  
                else:
                    result[key] = value  
            else:
                result[key] = value
    
    return result

def calculate_text_similarity(text1: str, text2: str) -> float:
    if not text1 or not text2:
        return 0.0
    
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def retry_operation(func, max_retries: int = 3, delay: float = 1.0):
    import time
    
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                    time.sleep(delay * (attempt + 1))  
                else:
                    logger.error(f"Operation failed after {max_retries + 1} attempts: {str(e)}")
        
        raise last_exception
    
    return wrapper

def create_directory_structure(base_path: str, structure: Dict[str, Any]) -> bool:
    try:
        base = Path(base_path)
        base.mkdir(parents=True, exist_ok=True)
        
        def create_items(current_path: Path, items: Dict[str, Any]):
            for name, content in items.items():
                item_path = current_path / name
                
                if isinstance(content, dict):
                    item_path.mkdir(exist_ok=True)
                    create_items(item_path, content)
                elif isinstance(content, str):
                    item_path.write_text(content, encoding='utf-8')
                else:
                    if name.endswith('/'):
                        item_path.mkdir(exist_ok=True)
                    else:
                        item_path.touch()
        
        create_items(base, structure)
        return True
        
    except Exception as e:
        logger.error(f"Error creating directory structure: {str(e)}")
        return False

def parse_time_string(time_str: str) -> Optional[datetime]:
    import re
    from dateutil import parser
    
    if not time_str:
        return None
    
    try:
        return parser.parse(time_str)
    except Exception:
        pass
    
    patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',  
        r'(\d{2})/(\d{2})/(\d{4})',  
        r'(\d{2})-(\d{2})-(\d{4})',  
    ]
    
    for pattern in patterns:
        match = re.search(pattern, time_str)
        if match:
            try:
                if pattern == patterns[0]:  
                    year, month, day = match.groups()
                else:  
                    month, day, year = match.groups()
                
                return datetime(int(year), int(month), int(day))
            except ValueError:
                continue
    
    return None

def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    code_blocks = []
    
    fenced_pattern = r'```(\w+)?\n(.*?)```'
    for match in re.finditer(fenced_pattern, text, re.DOTALL):
        language = match.group(1) or 'unknown'
        code = match.group(2).strip()
        
        code_blocks.append({
            'language': language,
            'code': code,
            'type': 'fenced',
            'start_pos': match.start(),
            'end_pos': match.end()
        })
    
    inline_pattern = r'`([^`\n]+)`'
    for match in re.finditer(inline_pattern, text):
        code = match.group(1).strip()
        
        if len(code) > 2:  
            code_blocks.append({
                'language': 'unknown',
                'code': code,
                'type': 'inline',
                'start_pos': match.start(),
                'end_pos': match.end()
            })
    
    return code_blocks

def normalize_path(path: Union[str, Path]) -> str:
    try:
        normalized = Path(path).resolve()
        return str(normalized).replace('\\', '/')
    except Exception:
        return str(path).replace('\\', '/')

def is_binary_file(file_path: Union[str, Path]) -> bool:
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            
        if b'\x00' in chunk:
            return True
        
        text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
        non_text = chunk.translate(None, text_chars)
        
        return len(non_text) / len(chunk) > 0.3
        
    except Exception:
        return True  

def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    import uuid
    import string
    import random
    
    chars = string.ascii_lowercase + string.digits
    random_part = ''.join(random.choices(chars, k=length))
    
    timestamp = str(int(datetime.now().timestamp()))[-6:]
    
    if prefix:
        return f"{prefix}_{timestamp}_{random_part}"
    else:
        return f"{timestamp}_{random_part}"

def deep_merge_config(base_config: Dict, override_config: Dict) -> Dict:
    import copy
    
    result = copy.deepcopy(base_config)
    
    def merge_recursive(base: Dict, override: Dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                merge_recursive(base[key], value)
            else:
                base[key] = value
    
    merge_recursive(result, override_config)
    return result

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return bool(re.match(pattern, email))

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)]
    
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  
        truncated = truncated[:last_space]
    
    return truncated + suffix

def create_backup_filename(original_path: Union[str, Path]) -> str:
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{path.stem}_backup_{timestamp}{path.suffix}"

def measure_execution_time(func):
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f} seconds: {str(e)}")
            raise
    
    return wrapper

def find_files_by_pattern(directory: Union[str, Path], pattern: str, recursive: bool = True) -> List[Path]:
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return []
    
    if recursive:
        return list(dir_path.rglob(pattern))
    else:
        return list(dir_path.glob(pattern))

def compress_whitespace(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: Union[int, float] = 0) -> Union[int, float]:
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ValueError):
        return default

def generate_user_hash(user_data: Dict[str, Any]) -> str:
    user_string = f"{user_data.get('email', '')}{user_data.get('name', '')}{datetime.now().date()}"
    return hashlib.md5(user_string.encode()).hexdigest()[:8]

def validate_user_session(session_data: Dict[str, Any]) -> bool:
    required_fields = ['user_id', 'expires_at']
    
    if not all(field in session_data for field in required_fields):
        return False
    
    try:
        expires_at = datetime.fromisoformat(session_data['expires_at'])
        return expires_at > datetime.now()
    except (ValueError, TypeError):
        return False

def filter_user_data(data: List[Dict[str, Any]], user_id: str, user_field: str = 'user_id') -> List[Dict[str, Any]]:
    return [item for item in data if item.get(user_field) == user_id]

def anonymize_user_data(data: Dict[str, Any], fields_to_anonymize: List[str] = None) -> Dict[str, Any]:
    if fields_to_anonymize is None:
        fields_to_anonymize = ['email', 'name', 'phone', 'address']
    
    anonymized = data.copy()
    
    for field in fields_to_anonymize:
        if field in anonymized:
            if field == 'email':
                anonymized[field] = 'user@example.com'
            elif field == 'name':
                anonymized[field] = 'Anonymous User'
            else:
                anonymized[field] = '[REDACTED]'
    
    return anonymized

def get_user_timezone_offset(timezone_str: str = None) -> int:
    try:
        if timezone_str:
            import pytz
            tz = pytz.timezone(timezone_str)
            return int(tz.utcoffset(datetime.now()).total_seconds() / 3600)
        return 0
    except Exception:
        return 0

def format_user_display_name(user_data: Dict[str, Any]) -> str:
    name = user_data.get('name', '').strip()
    email = user_data.get('email', '').strip()
    
    if name:
        return name
    elif email:
        return email.split('@')[0].replace('.', ' ').title()
    else:
        return 'Unknown User'

def create_user_context(user_data: Dict[str, Any], permissions: List[str] = None) -> Dict[str, Any]:
    return {
        'user_id': user_data.get('id'),
        'display_name': format_user_display_name(user_data),
        'email': user_data.get('email'),
        'is_demo': user_data.get('is_demo', False),
        'permissions': permissions or [],
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'last_activity': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def validate_user_permissions(user_context: Dict[str, Any], required_permission: str) -> bool:
    permissions = user_context.get('permissions', [])
    return required_permission in permissions or 'admin' in permissions

def mask_sensitive_data(text: str) -> str:
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, '[EMAIL]', text)
    
    phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b'
    text = re.sub(phone_pattern, '[PHONE]', text)
    
    return text

__all__ = [
    'get_file_hash',
    'extract_file_metadata', 
    'sanitize_text',
    'chunk_text_by_sentences',
    'extract_technical_terms',
    'estimate_reading_time',
    'format_file_size',
    'validate_file_path',
    'safe_json_load',
    'extract_urls',
    'clean_filename',
    'merge_dictionaries',
    'calculate_text_similarity',
    'retry_operation',
    'create_directory_structure',
    'parse_time_string',
    'extract_code_blocks',
    'normalize_path',
    'is_binary_file',
    'generate_unique_id',
    'deep_merge_config',
    'validate_email',
    'truncate_text',
    'create_backup_filename',
    'measure_execution_time',
    'find_files_by_pattern',
    'compress_whitespace',
    'safe_divide',
    'generate_user_hash',
    'validate_user_session',
    'filter_user_data',
    'anonymize_user_data',
    'get_user_timezone_offset',
    'format_user_display_name',
    'create_user_context',
    'validate_user_permissions',
    'mask_sensitive_data'
]