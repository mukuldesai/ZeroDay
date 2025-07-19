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
from dotenv import load_dotenv
load_dotenv()

class SlackParser:
    
    def __init__(self, config_path: str = None, demo_mode: bool = False, user_id: str = None):
        self.config = self._load_config(config_path)
        self.demo_mode = demo_mode
        self.user_id = user_id or "demo_user"
        self.users_map = {}
        self.channels_map = {}
        
        if self.demo_mode:
            self.demo_config = self._load_demo_config()
            logger.info(f"SlackParser initialized in DEMO mode for user: {self.user_id}")
        else:
            logger.info(f"SlackParser initialized in REAL mode for user: {self.user_id}")
        
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
                'scenarios': ['startup', 'enterprise', 'freelancer']
            }
    
    async def parse_slack_export(self, export_path: str = None, scenario: str = None) -> List[Dict[str, Any]]:
        if self.demo_mode:
            return await self._parse_demo_conversations(scenario)
        else:
            return await self._parse_real_export(export_path)
    
    async def _parse_demo_conversations(self, scenario: str = None) -> List[Dict[str, Any]]:
        logger.info(f"Generating DEMO Slack conversations for scenario: {scenario or 'default'}")
        
        demo_conversations = self._generate_synthetic_conversations(scenario)
        
        documents = []
        for conv_data in demo_conversations:
            conv_documents = self._process_demo_conversation(conv_data, scenario)
            documents.extend(conv_documents)
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': True,
                'demo_scenario': scenario or 'default',
                'user_id': self.user_id,
                'demo_note': 'This is synthetic demo data for showcase purposes'
            })
        
        logger.info(f"Generated {len(documents)} DEMO Slack documents")
        return documents
    
    async def _parse_real_export(self, export_path: str = None) -> List[Dict[str, Any]]:
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
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': False,
                'user_id': self.user_id
            })
        
        logger.info(f"Parsed {len(documents)} Slack message documents")
        return documents
    
    def _generate_synthetic_conversations(self, scenario: str = None) -> List[Dict[str, Any]]:
        startup_conversations = [
            {
                'channel': 'general',
                'messages': [
                    {'user': 'sarah-cto', 'text': 'Hey team! Just deployed the new authentication system to staging. Can everyone test their login flows?', 'ts': '1705823400'},
                    {'user': 'mike-frontend', 'text': 'Testing now! Login works great, logout seems smooth too', 'ts': '1705823460'},
                    {'user': 'jen-backend', 'text': 'Database connections are stable, seeing good performance on the auth queries', 'ts': '1705823520'},
                    {'user': 'sarah-cto', 'text': 'Awesome! If no issues by EOD, we\'ll push to production tomorrow morning', 'ts': '1705823580'}
                ]
            },
            {
                'channel': 'dev-team',
                'messages': [
                    {'user': 'mike-frontend', 'text': 'Running into a weird CSS issue with the dark mode toggle. The button stays highlighted after click', 'ts': '1705824000'},
                    {'user': 'alex-design', 'text': 'I think I know the issue! The :focus state isn\'t being cleared properly. Try adding `button:focus { outline: none; }`', 'ts': '1705824060'},
                    {'user': 'mike-frontend', 'text': '```css\n.dark-toggle:focus {\n  outline: none;\n  box-shadow: none;\n}\n```\nThis worked perfectly! Thanks Alex 🙌', 'ts': '1705824120'},
                    {'user': 'alex-design', 'text': 'No problem! Always happy to help with CSS mysteries 😄', 'ts': '1705824180'}
                ]
            }
        ]
        
        enterprise_conversations = [
            {
                'channel': 'platform-engineering',
                'messages': [
                    {'user': 'david-sre', 'text': 'Alert: API gateway is showing 15% increase in response times. Investigating now...', 'ts': '1705820000'},
                    {'user': 'lisa-platform', 'text': 'Checking the load balancer metrics. Seeing uneven distribution across backend pods', 'ts': '1705820060'},
                    {'user': 'david-sre', 'text': 'Found the issue! One of the backend services had a memory leak. Restarting the affected pods now', 'ts': '1705820240'},
                    {'user': 'marcus-security', 'text': 'Should we add this to our runbook? This is the third memory leak this quarter', 'ts': '1705820300'},
                    {'user': 'lisa-platform', 'text': 'Good point. I\'ll create a Confluence page with the detection and remediation steps', 'ts': '1705820360'}
                ]
            },
            {
                'channel': 'architecture-review',
                'messages': [
                    {'user': 'robert-architect', 'text': 'Reviewing the microservices migration proposal. The service boundaries look well-defined, but I have concerns about data consistency', 'ts': '1705821000'},
                    {'user': 'priya-lead', 'text': 'We\'re planning to use saga pattern for distributed transactions. Each service will publish events for state changes', 'ts': '1705821120'},
                    {'user': 'robert-architect', 'text': 'That\'s a solid approach. What about compensating actions if a step in the saga fails?', 'ts': '1705821180'},
                    {'user': 'priya-lead', 'text': 'Each service implements a rollback endpoint. The saga orchestrator tracks state and calls rollbacks in reverse order if needed', 'ts': '1705821240'},
                    {'user': 'robert-architect', 'text': 'Excellent! Please include the saga flow diagrams in the final RFC document', 'ts': '1705821300'}
                ]
            }
        ]
        
        freelancer_conversations = [
            {
                'channel': 'client-updates',
                'messages': [
                    {'user': 'emma-freelancer', 'text': 'Hi @client-john! Just finished implementing the shopping cart feature. You can test it at staging.yoursite.com', 'ts': '1705819000'},
                    {'user': 'client-john', 'text': 'This looks fantastic! The add-to-cart animation is really smooth. One small request - can we make the cart icon bounce when items are added?', 'ts': '1705819180'},
                    {'user': 'emma-freelancer', 'text': 'Absolutely! I\'ll add a subtle bounce animation. Should take about 30 minutes to implement', 'ts': '1705819240'},
                    {'user': 'client-john', 'text': 'Perfect! Also, my team loves the color scheme you chose. Much better than our old site', 'ts': '1705819300'},
                    {'user': 'emma-freelancer', 'text': 'Thank you! I\'ll have the cart animation ready for review this afternoon', 'ts': '1705819360'}
                ]
            }
        ]
        
        if scenario == 'enterprise':
            base_conversations = enterprise_conversations
        elif scenario == 'freelancer':
            base_conversations = freelancer_conversations
        else:
            base_conversations = startup_conversations
        
        result_conversations = []
        for i in range(len(base_conversations) * 2):
            base_conv = base_conversations[i % len(base_conversations)]
            conv_copy = base_conv.copy()
            conv_copy['messages'] = [msg.copy() for msg in conv_copy['messages']]
            result_conversations.append(conv_copy)
        
        return result_conversations
    
    def _process_demo_conversation(self, conv_data: Dict, scenario: str = None) -> List[Dict[str, Any]]:
        documents = []
        
        conversation_text = self._build_demo_conversation_text(conv_data['messages'])
        
        conv_doc = {
            'content': sanitize_text(conversation_text),
            'metadata': {
                'source_type': 'slack_conversation',
                'channel': conv_data['channel'],
                'channel_purpose': f"Demo {conv_data['channel']} channel",
                'is_private': False,
                'message_count': len(conv_data['messages']),
                'participants': list(set(msg['user'] for msg in conv_data['messages'])),
                'start_time': conv_data['messages'][0]['ts'],
                'end_time': conv_data['messages'][-1]['ts'],
                'date': self._format_date_from_timestamp(conv_data['messages'][0]['ts']),
                'content_hash': get_file_hash(conversation_text),
                'file_path': f"slack/{conv_data['channel']}/conv-{conv_data['messages'][0]['ts']}",
                'tags': self._extract_demo_conversation_tags(conv_data),
                'technical_terms': extract_technical_terms(conversation_text),
                'conversation_type': self._classify_conversation_type(conversation_text),
                'urgency': self._assess_urgency(conversation_text),
                'summary': self._summarize_demo_conversation(conv_data)
            }
        }
        documents.append(conv_doc)
        
        for message in conv_data['messages']:
            if self._is_demo_important_message(message):
                msg_doc = self._create_demo_message_document(message, conv_data['channel'])
                if msg_doc:
                    documents.append(msg_doc)
        
        return documents
    
    def _build_demo_conversation_text(self, messages: List[Dict]) -> str:
        lines = []
        
        for message in messages:
            timestamp = self._format_timestamp(message['ts'])
            username = message['user'].replace('-', ' ').title()
            text = message['text']
            
            lines.append(f"[{timestamp}] {username}: {text}")
        
        return '\n'.join(lines)
    
    def _summarize_demo_conversation(self, conv_data: Dict) -> str:
        participants = set(msg['user'] for msg in conv_data['messages'])
        channel = conv_data['channel']
        
        if 'dev' in channel or 'engineering' in channel:
            return f"Development discussion between {len(participants)} team members"
        elif 'client' in channel:
            return f"Client communication in {channel}"
        elif 'platform' in channel:
            return f"Platform engineering discussion"
        else:
            return f"Team conversation in #{channel}"
    
    def _extract_demo_conversation_tags(self, conv_data: Dict) -> List[str]:
        tags = ['slack', 'conversation', conv_data['channel']]
        
        conversation_text = ' '.join(msg['text'] for msg in conv_data['messages']).lower()
        
        if 'deploy' in conversation_text or 'production' in conversation_text:
            tags.append('deployment')
        if 'bug' in conversation_text or 'issue' in conversation_text:
            tags.append('bug')
        if 'css' in conversation_text or 'frontend' in conversation_text:
            tags.append('frontend')
        if 'api' in conversation_text or 'backend' in conversation_text:
            tags.append('backend')
        if 'client' in conv_data['channel']:
            tags.append('client_communication')
        
        return list(set(tags))
    
    def _is_demo_important_message(self, message: Dict) -> bool:
        text = message['text']
        
        if len(text) > 100:
            return True
        if '```' in text:
            return True
        if any(word in text.lower() for word in ['solution', 'fix', 'resolved', 'important']):
            return True
        
        return False
    
    def _create_demo_message_document(self, message: Dict, channel: str) -> Optional[Dict[str, Any]]:
        text = message['text']
        if not text.strip():
            return None
        
        clean_text = sanitize_text(text)
        username = message['user'].replace('-', ' ').title()
        
        return {
            'content': clean_text,
            'metadata': {
                'source_type': 'slack_message',
                'channel': channel,
                'author': username,
                'user_id': message['user'],
                'timestamp': message['ts'],
                'date': self._format_date_from_timestamp(message['ts']),
                'is_thread': False,
                'content_hash': get_file_hash(clean_text),
                'file_path': f"slack/{channel}/msg-{message['ts']}",
                'tags': self._extract_demo_message_tags(message, channel),
                'technical_terms': extract_technical_terms(clean_text),
                'has_code': '```' in text,
                'has_links': 'http' in text,
                'message_type': self._classify_message_type(text)
            }
        }
    
    def _extract_demo_message_tags(self, message: Dict, channel: str) -> List[str]:
        tags = ['slack', 'message', channel]
        
        text = message['text'].lower()
        
        if '```' in message['text']:
            tags.append('code')
        if 'http' in text:
            tags.append('link')
        if any(word in text for word in ['solution', 'fix', 'resolved']):
            tags.append('solution')
        
        return tags
    
    def _extract_zip(self, zip_path: Path, extract_dir: Path) -> Optional[Path]:
        try:
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r', encoding='utf-8') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            logger.info(f"Extracted Slack export to: {extract_dir}")
            return extract_dir
            
        except Exception as e:
            logger.error(f"Error extracting zip file: {str(e)}")
            return None
    
    def _load_metadata(self, export_dir: Path):
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
        text = message.get('text', '').lower()
        
        helpful_keywords = ['deploy', 'alert', 'error', 'warning', 'build', 'test', 'release']
        return any(keyword in text for keyword in helpful_keywords)
    
    def _is_meaningful_short_message(self, text: str) -> bool:
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
        user_info = self.users_map.get(user_id, {})
        return user_info.get('real_name') or user_info.get('name') or f'@{user_id}'
    
    def _format_timestamp(self, ts: str) -> str:
        try:
            dt = datetime.fromtimestamp(float(ts))
            return dt.strftime('%H:%M')
        except:
            return ts
    
    def _format_date_from_timestamp(self, ts: str) -> str:
        try:
            dt = datetime.fromtimestamp(float(ts))
            return dt.strftime('%Y-%m-%d')
        except:
            return 'unknown'
    
    def _summarize_conversation(self, conversation: List[Dict]) -> str:
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
        text_lower = conversation_text.lower()
        
        if any(word in text_lower for word in ['urgent', 'critical', 'emergency', 'asap', 'immediately']):
            return 'high'
        elif any(word in text_lower for word in ['important', 'priority', 'soon']):
            return 'medium'
        else:
            return 'low'
    
    def _is_important_message(self, message: Dict) -> bool:
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
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        return {
            "supported_formats": ["zip", "extracted_directory"],
            "demo_mode": self.demo_mode,
            "user_id": self.user_id,
            "demo_scenarios": self.get_demo_scenarios() if self.demo_mode else None,
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

if __name__ == "__main__":
      
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
            
            parser = SlackParser(demo_mode=demo_mode, user_id=user_id)
            
            if command == "parse":
                export_path = None
                for arg in sys.argv[2:]:
                    if not arg.startswith('--') and arg not in [user_id, scenario]:
                        export_path = arg
                        break
                
                if demo_mode and not export_path:
                    export_path = "demo_slack_export"
                
                results = await parser.parse_slack_export(export_path, scenario)
                print(f"Parsed {len(results)} Slack documents")
                
                if demo_mode:
                    print(f"Demo mode: {demo_mode}, Scenario: {scenario or 'default'}")
                
                for i, result in enumerate(results[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"Type: {result['metadata']['source_type']}")
                    print(f"Channel: {result['metadata']['channel']}")
                    print(f"Date: {result['metadata']['date']}")
                    print(f"Demo: {result['metadata'].get('is_demo', False)}")
                    print(f"Content: {result['content'][:100]}...")
                    
            elif command == "demo":
                print("Available demo scenarios:")
                for scenario in parser.get_demo_scenarios():
                    print(f"  - {scenario}")
                    
            elif command == "stats":
                stats = parser.get_parsing_stats()
                print("Slack Parser Statistics:")
                print(json.dumps(stats, indent=2))
                
            else:
                print("Available commands:")
                print("  parse [export_path] [--demo] [--user USER_ID] [--scenario SCENARIO] - Parse Slack export")
                print("  demo - Show available demo scenarios")
                print("  stats - Show parser capabilities")
        else:
            print("Usage: python slack_parser.py [parse|demo|stats] [options...]")
            print("Options:")
            print("  --demo              Enable demo mode")
            print("  --user USER_ID      Set user ID")
            print("  --scenario NAME     Set demo scenario (startup/enterprise/freelancer)")
    
    asyncio.run(main())