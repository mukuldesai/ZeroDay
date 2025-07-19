"""
Comprehensive Text Cleaner Utility
Handles Unicode issues, character encoding problems, and data sanitization
"""

import re
import unicodedata
import logging
from typing import Dict, List, Any, Union, Optional

class TextCleaner:
    """
    Comprehensive text cleaning utility to handle Unicode issues
    and character encoding problems throughout the ZeroDay application.
    """
    
    # Problematic characters found in the codebase
    PROBLEMATIC_CHARS = {
        '\x8f': '',       # Problematic byte
        '\x9f': '',       # Problematic byte
        '\x81': '',       # Problematic byte
        '\x9d': '',       # Problematic byte
        '\x8d': '',       # Problematic byte
        '\x90': '',       # Problematic byte
        '\x9c': '',       # Problematic byte
        '\x00': '',       # Null byte
        '\x0b': '',       # Vertical tab
        '\x0c': '',       # Form feed
        '\x0e': '',       # Shift out
        '\x0f': '',       # Shift in
        '\x10': '',       # Data link escape
        '\x11': '',       # Device control one
        '\x12': '',       # Device control two
        '\x13': '',       # Device control three
        '\x14': '',       # Device control four
        '\x15': '',       # Negative acknowledgement
        '\x16': '',       # Synchronous idle
        '\x17': '',       # End of transmission block
        '\x18': '',       # Cancel
        '\x19': '',       # End of medium
        '\x1a': '',       # Substitute
        '\x1b': '',       # Escape
        '\x1c': '',       # File separator
        '\x1d': '',       # Group separator
        '\x1e': '',       # Record separator
        '\x1f': '',       # Unit separator
        '\x7f': '',       # Delete
        # Smart quotes and similar problematic characters
        '\u2018': "'",    # Left single quotation mark
        '\u2019': "'",    # Right single quotation mark
        '\u201c': '"',    # Left double quotation mark
        '\u201d': '"',    # Right double quotation mark
        '\u2013': '-',    # En dash
        '\u2014': '-',    # Em dash
        '\u2026': '...',  # Horizontal ellipsis
        '\u00a0': ' ',    # Non-breaking space
    }
    
    # Safe characters: ASCII printable + essential whitespace
    SAFE_CHARS = set(range(32, 127)) | {9, 10, 13}  # Printable ASCII + tab, newline, carriage return
    
    @staticmethod
    def clean_text(content: Union[str, bytes, None], max_length: int = 5000) -> str:
        """
        Clean text content, handling various encoding issues.
        
        Args:
            content: Input text (str, bytes, or None)
            max_length: Maximum length of output (default: 5000)
            
        Returns:
            Cleaned text string
        """
        if not content:
            return ""
        
        try:
            # Step 1: Handle bytes input
            if isinstance(content, bytes):
                content = TextCleaner._decode_bytes(content)
            
            # Step 2: Convert to string
            content = str(content)
            
            # Step 3: Remove control characters except essential whitespace
            content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
            
            # Step 4: Replace specific problematic characters
            for bad_char, replacement in TextCleaner.PROBLEMATIC_CHARS.items():
                content = content.replace(bad_char, replacement)
            
            # Step 5: Unicode normalization
            content = unicodedata.normalize('NFKD', content)
            
            # Step 6: Filter to safe characters
            content = TextCleaner._filter_safe_chars(content)
            
            # Step 7: Limit length
            if len(content) > max_length:
                content = content[:max_length] + "..."
            
            # Step 8: Final validation
            content = content.strip()
            
            # Step 9: Test encode/decode to ensure it's safe
            content.encode('utf-8', errors='strict')
            
            return content
            
        except Exception as e:
            logging.warning(f"Text cleaning failed: {e}")
            # Ultra-safe fallback: ASCII only
            try:
                safe_content = ''.join(c for c in str(content) if 32 <= ord(c) <= 126)
                return safe_content[:1000] if safe_content else "content_unavailable"
            except:
                return "content_processing_failed"
    
    @staticmethod
    def _decode_bytes(content: bytes) -> str:
        """
        Decode bytes to string using multiple encoding attempts.
        
        Args:
            content: Bytes to decode
            
        Returns:
            Decoded string
        """
        # Try multiple encodings in order of preference
        encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii', 'utf-16']
        
        for encoding in encodings:
            try:
                return content.decode(encoding, errors='ignore')
            except (UnicodeDecodeError, LookupError):
                continue
        
        # Final fallback: decode as latin-1 with errors ignored
        return content.decode('latin-1', errors='ignore')
    
    @staticmethod
    def _filter_safe_chars(content: str) -> str:
        """
        Filter string to only include safe characters.
        
        Args:
            content: Input string
            
        Returns:
            Filtered string with only safe characters
        """
        safe_chars = []
        for char in content:
            char_code = ord(char)
            
            # Keep basic ASCII printable + essential whitespace
            if char_code in TextCleaner.SAFE_CHARS:
                safe_chars.append(char)
            # Keep some extended ASCII if they're safe
            elif 126 < char_code < 256:
                try:
                    # Test if character is safe to encode
                    test_encode = char.encode('utf-8', errors='strict')
                    if len(test_encode) <= 3:  # Reasonable UTF-8 sequence
                        safe_chars.append(char)
                except (UnicodeEncodeError, UnicodeDecodeError):
                    pass  # Skip problematic chars
        
        return ''.join(safe_chars)
    
    @staticmethod
    def clean_dict(data: Union[Dict[str, Any], None], max_depth: int = 5) -> Dict[str, Any]:
        """
        Clean dictionary recursively, handling nested structures.
        
        Args:
            data: Dictionary to clean
            max_depth: Maximum recursion depth
            
        Returns:
            Cleaned dictionary
        """
        if not isinstance(data, dict) or max_depth <= 0:
            return {}
        
        cleaned = {}
        for key, value in data.items():
            try:
                # Clean the key
                clean_key = TextCleaner.clean_text(str(key))
                
                # Clean the value based on type
                if isinstance(value, str):
                    cleaned[clean_key] = TextCleaner.clean_text(value)
                elif isinstance(value, dict):
                    cleaned[clean_key] = TextCleaner.clean_dict(value, max_depth - 1)
                elif isinstance(value, list):
                    cleaned[clean_key] = TextCleaner.clean_list(value, max_depth - 1)
                elif isinstance(value, (int, float, bool)):
                    cleaned[clean_key] = value
                elif value is None:
                    cleaned[clean_key] = None
                else:
                    # For other types, convert to string and clean
                    cleaned[clean_key] = TextCleaner.clean_text(str(value))
                    
            except Exception as e:
                logging.warning(f"Error cleaning dict item {key}: {e}")
                cleaned[str(key)] = "error_processing_value"
        
        return cleaned
    
    @staticmethod
    def clean_list(data: Union[List[Any], None], max_depth: int = 5, max_items: int = 20) -> List[Any]:
        """
        Clean list recursively, handling nested structures.
        
        Args:
            data: List to clean
            max_depth: Maximum recursion depth
            max_items: Maximum number of items to process
            
        Returns:
            Cleaned list
        """
        if not isinstance(data, list) or max_depth <= 0:
            return []
        
        cleaned = []
        for i, item in enumerate(data):
            if i >= max_items:
                break
                
            try:
                if isinstance(item, str):
                    cleaned.append(TextCleaner.clean_text(item))
                elif isinstance(item, dict):
                    cleaned.append(TextCleaner.clean_dict(item, max_depth - 1))
                elif isinstance(item, list):
                    cleaned.append(TextCleaner.clean_list(item, max_depth - 1, max_items))
                elif isinstance(item, (int, float, bool)):
                    cleaned.append(item)
                elif item is None:
                    cleaned.append(None)
                else:
                    # For other types, convert to string and clean
                    cleaned.append(TextCleaner.clean_text(str(item)))
                    
            except Exception as e:
                logging.warning(f"Error cleaning list item {i}: {e}")
                cleaned.append("error_processing_item")
        
        return cleaned
    
    @staticmethod
    def clean_any(data: Any, max_depth: int = 5) -> Any:
        """
        Clean any data type automatically.
        
        Args:
            data: Data to clean
            max_depth: Maximum recursion depth
            
        Returns:
            Cleaned data
        """
        if isinstance(data, str):
            return TextCleaner.clean_text(data)
        elif isinstance(data, dict):
            return TextCleaner.clean_dict(data, max_depth)
        elif isinstance(data, list):
            return TextCleaner.clean_list(data, max_depth)
        elif isinstance(data, (int, float, bool)):
            return data
        elif data is None:
            return None
        else:
            # For other types, convert to string and clean
            return TextCleaner.clean_text(str(data))
    
    @staticmethod
    def safe_json_dumps(data: Any, **kwargs) -> str:
        """
        Safely serialize data to JSON, cleaning it first.
        
        Args:
            data: Data to serialize
            **kwargs: Additional arguments for json.dumps
            
        Returns:
            JSON string
        """
        import json
        
        try:
            # Clean the data first
            cleaned_data = TextCleaner.clean_any(data)
            
            # Set safe defaults
            kwargs.setdefault('ensure_ascii', False)
            kwargs.setdefault('separators', (',', ':'))
            
            return json.dumps(cleaned_data, **kwargs)
            
        except Exception as e:
            logging.error(f"JSON serialization failed: {e}")
            return json.dumps({"error": "serialization_failed", "message": str(e)})
    
    @staticmethod
    def validate_clean_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean an API response.
        
        Args:
            response: Response dictionary
            
        Returns:
            Cleaned and validated response
        """
        if not isinstance(response, dict):
            return {
                "success": False,
                "error": "invalid_response_format",
                "response": "Invalid response format",
                "timestamp": TextCleaner._get_timestamp()
            }
        
        # Clean the entire response
        cleaned_response = TextCleaner.clean_dict(response)
        
        # Ensure required fields exist
        if "success" not in cleaned_response:
            cleaned_response["success"] = False
        
        if "timestamp" not in cleaned_response:
            cleaned_response["timestamp"] = TextCleaner._get_timestamp()
        
        if not cleaned_response.get("success") and "error" not in cleaned_response:
            cleaned_response["error"] = "unknown_error"
        
        return cleaned_response
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Convenience functions for backward compatibility
def clean_text(content: Union[str, bytes, None], max_length: int = 5000) -> str:
    """Convenience function for text cleaning."""
    return TextCleaner.clean_text(content, max_length)

def clean_dict(data: Union[Dict[str, Any], None]) -> Dict[str, Any]:
    """Convenience function for dict cleaning."""
    return TextCleaner.clean_dict(data)

def clean_list(data: Union[List[Any], None]) -> List[Any]:
    """Convenience function for list cleaning."""
    return TextCleaner.clean_list(data)

def clean_any(data: Any) -> Any:
    """Convenience function for cleaning any data type."""
    return TextCleaner.clean_any(data)


# Example usage and testing
if __name__ == "__main__":
    # Test problematic characters
    test_cases = [
        "Hello\x8fworld\x9f",  # Problematic bytes
        "Test\u2018quotes\u2019",  # Smart quotes
        b"bytes\x8f\x9fstring",  # Bytes input
        {"key\x8f": "value\x9f", "nested": {"inner\x81": "data\x9d"}},  # Dict
        ["item1\x8f", "item2\x9f", {"nested": "dict\x81"}],  # List
    ]
    
    print("Testing TextCleaner:")
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {type(test_case).__name__}")
        print(f"Input: {repr(test_case)}")
        
        if isinstance(test_case, str) or isinstance(test_case, bytes):
            result = TextCleaner.clean_text(test_case)
        elif isinstance(test_case, dict):
            result = TextCleaner.clean_dict(test_case)
        elif isinstance(test_case, list):
            result = TextCleaner.clean_list(test_case)
        else:
            result = TextCleaner.clean_any(test_case)
        
        print(f"Output: {repr(result)}")
        print(f"Type: {type(result).__name__}")