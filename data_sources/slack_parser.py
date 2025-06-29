import os
import yaml
import json
import zipfile
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, sanitize_text, extract_technical_terms

class SlackParser:
    """
    Slack Parser: Processes Slack workspace exports
    Extracts messages, threads, and team conversations for knowledge indexing
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.users_map = {}
        self.channels_map = {}
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def parse_slack_export(self, export_path: str = None) -> List[Dict[str, Any]]:
        """
        Parse Slack workspace export
        
        Args:
            export_path: Path to Slack export (zip file or extracted directory)
            
        Returns:
            List of processed message documents
        """
        if not export_path:
            export_path = self.config['data_sources']['slack_export']['path']
        
        export_path = Path(export_path)
        
        if not export_path.exists():
            logger.warning(f"Slack export path does not exist: {export_path}")
            return []
        
        logger.info(f"Starting Slack export parsing from: {export_path}")
        
        
        if export_path.suffix.lower() == '.zip':
            extract_dir = export_path.parent / f"{export_path.stem}_extracted"
            export_path = self._extract_zip(export_path, extract_dir)
        
        if not export_path or not export_path.exists():
            logger.error("Failed to extract or locate Slack export")
            return []
        
        documents = []
        
        try:
           
            self._load_metadata(export_path)
            
           
            channels_dir = export_path
            for channel_dir in channels_dir.iterdir():
                if channel_dir.is_dir() and not channel_dir.name.startswith('.'):
                    channel_docs = await self._process_channel(channel_dir)
                    documents.extend(channel_docs)
        
        except Exception as e:
            logger.error(f"Error parsing Slack export: {str(e)}")
            return []
        
        logger.info(f"Parsed {len(documents)} Slack message documents")
        return documents
    
    def _extract_zip(self, zip_path: Path, extract_dir: Path) -> Optional[Path]:
        """Extract Slack export zip file"""
        try:
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            logger.info(f"Extracted Slack export to: {extract_dir}")
            return extract_dir
            
        except Exception as e:
            logger.error(f"Error extracting zip file: {str(e)}")
            return None
    
    def _load_metadata(self, export_dir: Path):
        """Load users and channels metadata"""
        try:
          
            users_file = export_dir / "users.json"
            if users_file.exists():
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
                    self.users_map = {user['id']: user for user in users}
                    logger.info(f"Loaded {len(self.users_map)} users")
            
         
            channels_file = export_dir / "channels.json"
            if channels_file.exists():
                with open(channels_file, 'r', encoding='utf-8') as f:
                    channels = json.load(f)
                    self.channels_map = {channel['id']: channel for channel in channels}
                    logger.info(f"Loaded {len(self.channels_map)} channels")
        
        except Exception as e:
            logger.warning(f"Error loading metadata: {str(e)}")
    
    async def _process_channel(self, channel_dir: Path) -> List[Dict[str, Any]]:
        """Process messages from a single channel"""
        documents = []
        channel_name = channel_dir.name
        
        
        channel_info = self._get_channel_info(channel_name)
        
        try:
          
            json_files = list(channel_dir.glob("*.json"))
            
            for json_file in json_files:
                with open(json_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                
               
                conversations = self._group_messages_into_conversations(messages)
                
                for conversation in conversations:
                    conv_docs = self._process_conversation(conversation, channel_name, channel_info)
                    documents.extend(conv_docs)
        
        except Exception as e:
            logger.error(f"Error processing channel {channel_name}: {str(e)}")
        
        return documents
    
    def _get_channel_info(self, channel_name: str) -> Dict[str, Any]:
        """Get channel information from metadata"""
        
        for channel_id, channel_data in self.channels_map.items():
            if channel_data.get('name') == channel_name:
                return channel_data
        
        
        return {
            'name': channel_name,
            'purpose': {'value': ''},
            'topic': {'value': ''},
            'is_private': False
        }
    
    def _group_messages_into_conversations(self, messages: List[Dict]) -> List[List[Dict]]:
        """Group messages into conversations based on time gaps and threads"""
        if not messages:
            return []
        
       
        sorted_messages = sorted(messages, key=lambda x: float(x.get('ts', 0)))
        
        conversations = []
        current_conversation = []
        conversation_timeout = 3600  
        
        for message in sorted_messages:
           
            if self._should_skip_message(message):
                continue
            
            
            if current_conversation:
                last_ts = float(current_conversation[-1].get('ts', 0))
                current_ts = float(message.get('ts', 0))
                
                if current_ts - last_ts > conversation_timeout:
                   
                    if len(current_conversation) >= 2:  
                        conversations.append(current_conversation)
                    current_conversation = [message]
                else:
                    current_conversation.append(message)
            else:
                current_conversation.append(message)
        
        
        if len(current_conversation) >= 2:
            conversations.append(current_conversation)
        
        return conversations
    
    def _should_skip_message(self, message: Dict) -> bool:
        """Determine if a message should be skipped"""
        
        if message.get('bot_id') and not self._is_helpful_bot_message(message):
            return True
        
        
        if message.get('subtype') in ['channel_join', 'channel_leave', 'channel_topic', 'channel_purpose']:
            return True
        
        
        if not message.get('text', '').strip():
            return True
        
       
        text = message.get('text', '').strip()
        if len(text) < 10 and not self._is_meaningful_short_message(text):
            return True
        
        return False
    
    def _is_helpful_bot_message(self, message: Dict) -> bool:
        """Check if bot message contains helpful information"""
        text = message.get('text', '').lower()
        
        
        helpful_keywords = ['deploy', 'alert', 'error', 'warning', 'build', 'test', 'release']
        return any(keyword in text for keyword in helpful_keywords)
    
    def _is_meaningful_short_message(self, text: str) -> bool:
        """Check if short message is meaningful"""
        meaningful_patterns = [
            r'thanks?!?',
            r'lgtm',
            r'approved?',
            r'fixed?',
            r'done',
            r'yes|no',
            r':\+1:|👍',
            r':\-1:|👎'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in meaningful_patterns)
    
    def _process_conversation(
        self, 
        conversation: List[Dict], 
        channel_name: str, 
        channel_info: Dict
    ) -> List[Dict[str, Any]]:
        """Process a conversation into documents"""
        
        if len(conversation) < 2:
            return []
        
        documents = []
        
        
        
        conversation_text = self._build_conversation_text(conversation)
        conversation_summary = self._summarize_conversation(conversation)
        
        
        conv_doc = {
            'content': sanitize_text(conversation_text),
            'metadata': {
                'source_type': 'slack_conversation',
                'channel': channel_name,
                'channel_purpose': channel_info.get('purpose', {}).get('value', ''),
                'is_private': channel_info.get('is_private', False),
                'message_count': len(conversation),
                'participants': list(set(msg.get('user', 'unknown') for msg in conversation)),
                'start_time': conversation[0].get('ts'),
                'end_time': conversation[-1].get('ts'),
                'date': self._format_date_from_timestamp(conversation[0].get('ts')),
                'content_hash': get_file_hash(conversation_text),
                'file_path': f"slack/{channel_name}/conv-{conversation[0].get('ts')}",
                'tags': self._extract_conversation_tags(conversation, channel_name),
                'technical_terms': extract_technical_terms(conversation_text),
                'conversation_type': self._classify_conversation_type(conversation_text),
                'urgency': self._assess_urgency(conversation_text),
                'summary': conversation_summary
            }
        }
        documents.append(conv_doc)
        
        
        for message in conversation:
            if self._is_important_message(message):
                msg_doc = self._create_message_document(message, channel_name, channel_info)
                if msg_doc:
                    documents.append(msg_doc)
        
        return documents
    
    def _build_conversation_text(self, conversation: List[Dict]) -> str:
        """Build readable conversation text"""
        lines = []
        
        for message in conversation:
            user_info = self.users_map.get(message.get('user', ''), {})
            username = user_info.get('real_name') or user_info.get('name') or 'Unknown User'
            
            timestamp = self._format_timestamp(message.get('ts'))
            text = self._clean_message_text(message.get('text', ''))
            
            lines.append(f"[{timestamp}] {username}: {text}")
            
            
            if message.get('thread_ts') and message.get('replies'):
                for reply in message.get('replies', []):
                    reply_user = self.users_map.get(reply.get('user', ''), {})
                    reply_username = reply_user.get('real_name') or reply_user.get('name') or 'Unknown User'
                    reply_text = self._clean_message_text(reply.get('text', ''))
                    lines.append(f"  └─ {reply_username}: {reply_text}")
        
        return '\n'.join(lines)
    
    def _clean_message_text(self, text: str) -> str:
        """Clean Slack message text"""
        if not text:
            return ""
        
        
        text = re.sub(r'<@([A-Z0-9]+)>', lambda m: self._get_user_name(m.group(1)), text)
        
       
        text = re.sub(r'<#([A-Z0-9]+)\|([^>]+)>', r'#\2', text)
        
        
        text = re.sub(r'<([^|>]+)\|([^>]+)>', r'\2 (\1)', text)
        text = re.sub(r'<([^>]+)>', r'\1', text)
        
        
        text = re.sub(r'```([^`]+)```', r'[code: \1]', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'[\1]', text)
        
        return text.strip()
    
    def _get_user_name(self, user_id: str) -> str:
        """Get readable user name from ID"""
        user_info = self.users_map.get(user_id, {})
        return user_info.get('real_name') or user_info.get('name') or f'@{user_id}'
    
    def _format_timestamp(self, ts: str) -> str:
        """Format Slack timestamp to readable format"""
        try:
            dt = datetime.fromtimestamp(float(ts))
            return dt.strftime('%H:%M')
        except:
            return ts
    
    def _format_date_from_timestamp(self, ts: str) -> str:
        """Format timestamp to date"""
        try:
            dt = datetime.fromtimestamp(float(ts))
            return dt.strftime('%Y-%m-%d')
        except:
            return 'unknown'
    
    def _summarize_conversation(self, conversation: List[Dict]) -> str:
        """Create a brief summary of the conversation"""
        if len(conversation) <= 2:
            return "Brief exchange between team members"
        
        participants = set()
        topics = []
        
        for message in conversation:
            user_info = self.users_map.get(message.get('user', ''), {})
            username = user_info.get('real_name') or user_info.get('name') or 'team member'
            participants.add(username)
            
           
            text = message.get('text', '').lower()
            if any(word in text for word in ['problem', 'issue', 'error', 'bug']):
                topics.append('troubleshooting')
            elif any(word in text for word in ['deploy', 'release', 'launch']):
                topics.append('deployment')
            elif any(word in text for word in ['review', 'feedback', 'opinion']):
                topics.append('code review')
            elif any(word in text for word in ['help', 'question', 'how']):
                topics.append('help request')
        
        participant_str = f"{len(participants)} team members"
        topic_str = f" discussing {', '.join(set(topics))}" if topics else ""
        
        return f"Conversation between {participant_str}{topic_str}"
    
    def _extract_conversation_tags(self, conversation: List[Dict], channel_name: str) -> List[str]:
        """Extract tags from conversation"""
        tags = ['slack', 'conversation', channel_name]
        
        conversation_text = ' '.join(msg.get('text', '') for msg in conversation).lower()
        
        
        tech_keywords = {
            'deployment': ['deploy', 'release', 'production', 'staging'],
            'bug': ['bug', 'error', 'issue', 'problem'],
            'feature': ['feature', 'new', 'implement', 'add'],
            'review': ['review', 'feedback', 'lgtm', 'approve'],
            'help': ['help', 'question', 'how', 'stuck'],
            'meeting': ['meeting', 'standup', 'sync', 'call']
        }
        
        for tag, keywords in tech_keywords.items():
            if any(keyword in conversation_text for keyword in keywords):
                tags.append(tag)
        
        
        if 'general' in channel_name:
            tags.append('general_discussion')
        elif 'dev' in channel_name or 'engineering' in channel_name:
            tags.append('development')
        elif 'support' in channel_name or 'help' in channel_name:
            tags.append('support')
        
        return list(set(tags))
    
    def _classify_conversation_type(self, conversation_text: str) -> str:
        """Classify the type of conversation"""
        text_lower = conversation_text.lower()
        
        if any(word in text_lower for word in ['error', 'bug', 'broken', 'issue', 'problem']):
            return 'troubleshooting'
        elif any(word in text_lower for word in ['deploy', 'release', 'production']):
            return 'deployment'
        elif any(word in text_lower for word in ['review', 'feedback', 'lgtm']):
            return 'code_review'
        elif any(word in text_lower for word in ['meeting', 'standup', 'sync']):
            return 'coordination'
        elif any(word in text_lower for word in ['help', 'question', 'how']):
            return 'help_request'
        elif any(word in text_lower for word in ['announcement', 'update', 'fyi']):
            return 'announcement'
        else:
            return 'general_discussion'
    
    def _assess_urgency(self, conversation_text: str) -> str:
        """Assess conversation urgency"""
        text_lower = conversation_text.lower()
        
        if any(word in text_lower for word in ['urgent', 'critical', 'emergency', 'asap', 'immediately']):
            return 'high'
        elif any(word in text_lower for word in ['important', 'priority', 'soon']):
            return 'medium'
        else:
            return 'low'
    
    def _is_important_message(self, message: Dict) -> bool:
        """Determine if a message is important enough for individual indexing"""
        text = message.get('text', '').lower()
        
        
        if len(text) > 200:
            return True
        
       
        if '```' in message.get('text', '') or '`' in message.get('text', ''):
            return True
        
        
        important_keywords = [
            'solution', 'fix', 'resolved', 'workaround', 'documentation',
            'guide', 'tutorial', 'example', 'important', 'note'
        ]
        
        if any(keyword in text for keyword in important_keywords):
            return True
        
        
        if message.get('attachments') or '<http' in message.get('text', ''):
            return True
        
        return False
    
    def _create_message_document(self, message: Dict, channel_name: str, channel_info: Dict) -> Optional[Dict[str, Any]]:
        """Create document for individual important message"""
        text = message.get('text', '')
        if not text.strip():
            return None
        
        clean_text = sanitize_text(self._clean_message_text(text))
        
        user_info = self.users_map.get(message.get('user', ''), {})
        username = user_info.get('real_name') or user_info.get('name') or 'Unknown User'
        
        return {
            'content': clean_text,
            'metadata': {
                'source_type': 'slack_message',
                'channel': channel_name,
                'author': username,
                'user_id': message.get('user', 'unknown'),
                'timestamp': message.get('ts'),
                'date': self._format_date_from_timestamp(message.get('ts')),
                'is_thread': bool(message.get('thread_ts')),
                'content_hash': get_file_hash(clean_text),
                'file_path': f"slack/{channel_name}/msg-{message.get('ts')}",
                'tags': self._extract_message_tags(message, channel_name),
                'technical_terms': extract_technical_terms(clean_text),
                'has_code': '```' in text or '`' in text,
                'has_links': '<http' in text,
                'message_type': self._classify_message_type(text)
            }
        }
    
    def _extract_message_tags(self, message: Dict, channel_name: str) -> List[str]:
        """Extract tags from individual message"""
        tags = ['slack', 'message', channel_name]
        
        text = message.get('text', '').lower()
        
        if '```' in message.get('text', ''):
            tags.append('code')
        if 'http' in text:
            tags.append('link')
        if message.get('thread_ts'):
            tags.append('thread')
        if any(word in text for word in ['solution', 'fix', 'resolved']):
            tags.append('solution')
        
        return tags
    
    def _classify_message_type(self, text: str) -> str:
        """Classify individual message type"""
        text_lower = text.lower()
        
        if '```' in text:
            return 'code_share'
        elif any(word in text_lower for word in ['solution', 'fix', 'resolved']):
            return 'solution'
        elif text_lower.endswith('?'):
            return 'question'
        elif any(word in text_lower for word in ['thanks', 'thank you']):
            return 'acknowledgment'
        elif 'http' in text_lower:
            return 'link_share'
        else:
            return 'discussion'
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get parser statistics and capabilities"""
        return {
            "supported_formats": ["zip", "extracted_directory"],
            "processed_data_types": [
                "channel_messages",
                "threaded_conversations",
                "user_mentions",
                "code_snippets",
                "shared_links"
            ],
            "filtering_features": [
                "bot_message_filtering",
                "system_message_exclusion",
                "conversation_grouping",
                "importance_detection"
            ],
            "metadata_extraction": [
                "user_mapping",
                "channel_information",
                "timestamp_processing",
                "thread_relationships"
            ],
            "users_loaded": len(self.users_map),
            "channels_loaded": len(self.channels_map)
        }


def parse_slack_quick(export_path: str) -> List[Dict[str, Any]]:
    """Quick Slack parsing function"""
    parser = SlackParser()
    import asyncio
    return asyncio.run(parser.parse_slack_export(export_path))

if __name__ == "__main__":
    
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            parser = SlackParser()
            
            if command == "parse":
                export_path = sys.argv[2] if len(sys.argv) > 2 else None
                
                if not export_path:
                    print("Usage: python slack_parser.py parse <export_path>")
                    return
                
                results = await parser.parse_slack_export(export_path)
                print(f"Parsed {len(results)} Slack documents")
                
                
                for i, result in enumerate(results[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"Type: {result['metadata']['source_type']}")
                    print(f"Channel: {result['metadata']['channel']}")
                    print(f"Date: {result['metadata']['date']}")
                    print(f"Content: {result['content'][:100]}...")
                    
            elif command == "stats":
                stats = parser.get_parsing_stats()
                print("Slack Parser Statistics:")
                print(json.dumps(stats, indent=2))
                
            else:
                print("Available commands:")
                print("  parse <export_path> - Parse Slack workspace export")
                print("  stats - Show parser capabilities")
        else:
            print("Usage: python slack_parser.py [parse|stats] [args...]")
    
    asyncio.run(main())