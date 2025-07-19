import os
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, sanitize_text, extract_technical_terms

class DemoSlack:
    
    def __init__(self, config_path: str = None, user_id: str = None):
        self.config = self._load_config(config_path)
        self.user_id = user_id or "demo_user"
        
    def _load_config(self, config_path: str = None) -> Dict:
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "demo_settings.yaml"
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {'scenarios': ['startup', 'enterprise', 'freelancer']}
    
    def generate_workspace_data(self, scenario: str = None) -> Dict[str, Any]:
        scenario = scenario or 'startup'
        
        return {
            'workspace': self._get_workspace_info(scenario),
            'users': self._generate_users(scenario),
            'channels': self._generate_channels(scenario),
            'conversations': self._generate_conversations(scenario),
            'messages': self._generate_individual_messages(scenario)
        }
    
    def _get_workspace_info(self, scenario: str) -> Dict[str, Any]:
        workspace_names = {
            'startup': 'TechStart Workspace',
            'enterprise': 'Enterprise Corp',
            'freelancer': 'Freelance Hub'
        }
        
        return {
            'id': f'T{scenario.upper()}123456',
            'name': workspace_names.get(scenario, workspace_names['startup']),
            'domain': f'{scenario}-demo',
            'url': f'https://{scenario}-demo.slack.com/',
            'created': int((datetime.now() - timedelta(days=365)).timestamp()),
            'icon': {
                'image_default': True
            }
        }
    
    def _generate_users(self, scenario: str) -> List[Dict[str, Any]]:
        if scenario == 'enterprise':
            return self._enterprise_users()
        elif scenario == 'freelancer':
            return self._freelancer_users()
        else:
            return self._startup_users()
    
    def _startup_users(self) -> List[Dict[str, Any]]:
        return [
            {
                'id': 'U001',
                'name': 'sarah.cto',
                'real_name': 'Sarah Chen',
                'display_name': 'Sarah (CTO)',
                'title': 'Chief Technology Officer',
                'profile': {
                    'email': 'sarah@startup.com',
                    'phone': '+1-555-0101',
                    'image_24': 'https://avatars.slack-edge.com/sarah_24.jpg',
                    'image_48': 'https://avatars.slack-edge.com/sarah_48.jpg'
                },
                'is_admin': True,
                'is_bot': False,
                'deleted': False
            },
            {
                'id': 'U002',
                'name': 'mike.frontend',
                'real_name': 'Mike Rodriguez',
                'display_name': 'Mike',
                'title': 'Frontend Developer',
                'profile': {
                    'email': 'mike@startup.com',
                    'phone': '+1-555-0102',
                    'image_24': 'https://avatars.slack-edge.com/mike_24.jpg',
                    'image_48': 'https://avatars.slack-edge.com/mike_48.jpg'
                },
                'is_admin': False,
                'is_bot': False,
                'deleted': False
            },
            {
                'id': 'U003',
                'name': 'jen.backend',
                'real_name': 'Jennifer Kim',
                'display_name': 'Jen',
                'title': 'Backend Developer',
                'profile': {
                    'email': 'jen@startup.com',
                    'phone': '+1-555-0103',
                    'image_24': 'https://avatars.slack-edge.com/jen_24.jpg',
                    'image_48': 'https://avatars.slack-edge.com/jen_48.jpg'
                },
                'is_admin': False,
                'is_bot': False,
                'deleted': False
            },
            {
                'id': 'U004',
                'name': 'alex.design',
                'real_name': 'Alex Thompson',
                'display_name': 'Alex',
                'title': 'UI/UX Designer',
                'profile': {
                    'email': 'alex@startup.com',
                    'phone': '+1-555-0104',
                    'image_24': 'https://avatars.slack-edge.com/alex_24.jpg',
                    'image_48': 'https://avatars.slack-edge.com/alex_48.jpg'
                },
                'is_admin': False,
                'is_bot': False,
                'deleted': False
            }
        ]
    
    def _enterprise_users(self) -> List[Dict[str, Any]]:
        return [
            {
                'id': 'U101',
                'name': 'david.sre',
                'real_name': 'David Wilson',
                'display_name': 'David (SRE)',
                'title': 'Site Reliability Engineer',
                'profile': {
                    'email': 'david.wilson@enterprise.com',
                    'phone': '+1-555-1001',
                    'image_24': 'https://avatars.slack-edge.com/david_24.jpg',
                    'image_48': 'https://avatars.slack-edge.com/david_48.jpg'
                },
                'is_admin': False,
                'is_bot': False,
                'deleted': False
            },
            {
                'id': 'U102',
                'name': 'lisa.platform',
                'real_name': 'Lisa Garcia',
                'display_name': 'Lisa',
                'title': 'Platform Engineer',
                'profile': {
                    'email': 'lisa.garcia@enterprise.com',
                    'phone': '+1-555-1002',
                    'image_24': 'https://avatars.slack-edge.com/lisa_24.jpg',
                    'image_48': 'https://avatars.slack-edge.com/lisa_48.jpg'
                },
                'is_admin': False,
                'is_bot': False,
                'deleted': False
            },
            {
                'id': 'U103',
                'name': 'robert.architect',
                'real_name': 'Robert Chen',
                'display_name': 'Robert',
                'title': 'Principal Architect',
                'profile': {
                    'email': 'robert.chen@enterprise.com',
                    'phone': '+1-555-1003',
                    'image_24': 'https://avatars.slack-edge.com/robert_24.jpg',
                    'image_48': 'https://avatars.slack-edge.com/robert_48.jpg'
                },
                'is_admin': True,
                'is_bot': False,
                'deleted': False
            }
        ]
    
    def _freelancer_users(self) -> List[Dict[str, Any]]:
        return [
            {
                'id': 'U201',
                'name': 'emma.freelancer',
                'real_name': 'Emma Johnson',
                'display_name': 'Emma',
                'title': 'Full Stack Developer',
                'profile': {
                    'email': 'emma@freelancer.com',
                    'phone': '+1-555-2001',
                    'image_24': 'https://avatars.slack-edge.com/emma_24.jpg',
                    'image_48': 'https://avatars.slack-edge.com/emma_48.jpg'
                },
                'is_admin': True,
                'is_bot': False,
                'deleted': False
            },
            {
                'id': 'U202',
                'name': 'client.john',
                'real_name': 'John Smith',
                'display_name': 'John (Client)',
                'title': 'Product Manager',
                'profile': {
                    'email': 'john@client.com',
                    'phone': '+1-555-2002',
                    'image_24': 'https://avatars.slack-edge.com/john_24.jpg',
                    'image_48': 'https://avatars.slack-edge.com/john_48.jpg'
                },
                'is_admin': False,
                'is_bot': False,
                'deleted': False
            }
        ]
    
    def _generate_channels(self, scenario: str) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        if scenario == 'enterprise':
            channels = [
                {
                    'id': 'C101',
                    'name': 'platform-engineering',
                    'is_channel': True,
                    'is_private': False,
                    'is_archived': False,
                    'creator': 'U103',
                    'created': int((base_date - timedelta(days=180)).timestamp()),
                    'purpose': {'value': 'Platform engineering discussions and alerts'},
                    'topic': {'value': 'Current focus: microservices migration Q2'},
                    'num_members': 12
                },
                {
                    'id': 'C102',
                    'name': 'architecture-review',
                    'is_channel': True,
                    'is_private': True,
                    'is_archived': False,
                    'creator': 'U103',
                    'created': int((base_date - timedelta(days=120)).timestamp()),
                    'purpose': {'value': 'Architecture decisions and design reviews'},
                    'topic': {'value': 'RFC reviews and technical discussions'},
                    'num_members': 8
                }
            ]
        elif scenario == 'freelancer':
            channels = [
                {
                    'id': 'C201',
                    'name': 'client-updates',
                    'is_channel': True,
                    'is_private': False,
                    'is_archived': False,
                    'creator': 'U201',
                    'created': int((base_date - timedelta(days=90)).timestamp()),
                    'purpose': {'value': 'Project updates and client communication'},
                    'topic': {'value': 'Website redesign project - Phase 2'},
                    'num_members': 3
                }
            ]
        else:
            channels = [
                {
                    'id': 'C001',
                    'name': 'general',
                    'is_channel': True,
                    'is_private': False,
                    'is_archived': False,
                    'creator': 'U001',
                    'created': int((base_date - timedelta(days=200)).timestamp()),
                    'purpose': {'value': 'Company-wide announcements and general discussion'},
                    'topic': {'value': 'Welcome to our startup! 🚀'},
                    'num_members': 15
                },
                {
                    'id': 'C002',
                    'name': 'dev-team',
                    'is_channel': True,
                    'is_private': False,
                    'is_archived': False,
                    'creator': 'U001',
                    'created': int((base_date - timedelta(days=180)).timestamp()),
                    'purpose': {'value': 'Development team coordination and technical discussions'},
                    'topic': {'value': 'Sprint 12 - Authentication system implementation'},
                    'num_members': 8
                }
            ]
        
        return channels
    
    def _generate_conversations(self, scenario: str) -> List[Dict[str, Any]]:
        if scenario == 'enterprise':
            return self._enterprise_conversations()
        elif scenario == 'freelancer':
            return self._freelancer_conversations()
        else:
            return self._startup_conversations()
    
    def _startup_conversations(self) -> List[Dict[str, Any]]:
        base_ts = int(datetime.now().timestamp())
        
        return [
            {
                'channel': 'general',
                'messages': [
                    {
                        'type': 'message',
                        'user': 'U001',
                        'text': 'Hey team! Just deployed the new authentication system to staging. Can everyone test their login flows?',
                        'ts': str(base_ts - 3600)
                    },
                    {
                        'type': 'message',
                        'user': 'U002',
                        'text': 'Testing now! Login works great, logout seems smooth too :+1:',
                        'ts': str(base_ts - 3540)
                    },
                    {
                        'type': 'message',
                        'user': 'U003',
                        'text': 'Database connections are stable, seeing good performance on the auth queries',
                        'ts': str(base_ts - 3480)
                    },
                    {
                        'type': 'message',
                        'user': 'U001',
                        'text': 'Awesome! If no issues by EOD, we\'ll push to production tomorrow morning :rocket:',
                        'ts': str(base_ts - 3420)
                    }
                ]
            },
            {
                'channel': 'dev-team',
                'messages': [
                    {
                        'type': 'message',
                        'user': 'U002',
                        'text': 'Running into a weird CSS issue with the dark mode toggle. The button stays highlighted after click',
                        'ts': str(base_ts - 7200)
                    },
                    {
                        'type': 'message',
                        'user': 'U004',
                        'text': 'I think I know the issue! The :focus state isn\'t being cleared properly. Try adding `button:focus { outline: none; }`',
                        'ts': str(base_ts - 7140)
                    },
                    {
                        'type': 'message',
                        'user': 'U002',
                        'text': '```css\n.dark-toggle:focus {\n  outline: none;\n  box-shadow: none;\n}\n```\nThis worked perfectly! Thanks Alex :raised_hands:',
                        'ts': str(base_ts - 7080)
                    },
                    {
                        'type': 'message',
                        'user': 'U004',
                        'text': 'No problem! Always happy to help with CSS mysteries :smile:',
                        'ts': str(base_ts - 7020)
                    }
                ]
            }
        ]
    
    def _enterprise_conversations(self) -> List[Dict[str, Any]]:
        base_ts = int(datetime.now().timestamp())
        
        return [
            {
                'channel': 'platform-engineering',
                'messages': [
                    {
                        'type': 'message',
                        'user': 'U101',
                        'text': ':warning: Alert: API gateway is showing 15% increase in response times. Investigating now...',
                        'ts': str(base_ts - 5400)
                    },
                    {
                        'type': 'message',
                        'user': 'U102',
                        'text': 'Checking the load balancer metrics. Seeing uneven distribution across backend pods',
                        'ts': str(base_ts - 5340)
                    },
                    {
                        'type': 'message',
                        'user': 'U101',
                        'text': 'Found the issue! One of the backend services had a memory leak. Restarting the affected pods now',
                        'ts': str(base_ts - 5160)
                    },
                    {
                        'type': 'message',
                        'user': 'U102',
                        'text': 'Response times back to normal. Adding this to our monitoring dashboard for early detection',
                        'ts': str(base_ts - 5100)
                    }
                ]
            },
            {
                'channel': 'architecture-review',
                'messages': [
                    {
                        'type': 'message',
                        'user': 'U103',
                        'text': 'Reviewing the microservices migration proposal. The service boundaries look well-defined, but I have concerns about data consistency',
                        'ts': str(base_ts - 10800)
                    },
                    {
                        'type': 'message',
                        'user': 'U102',
                        'text': 'We\'re planning to use saga pattern for distributed transactions. Each service will publish events for state changes',
                        'ts': str(base_ts - 10680)
                    },
                    {
                        'type': 'message',
                        'user': 'U103',
                        'text': 'That\'s a solid approach. What about compensating actions if a step in the saga fails?',
                        'ts': str(base_ts - 10620)
                    },
                    {
                        'type': 'message',
                        'user': 'U102',
                        'text': 'Each service implements a rollback endpoint. The saga orchestrator tracks state and calls rollbacks in reverse order if needed',
                        'ts': str(base_ts - 10560)
                    }
                ]
            }
        ]
    
    def _freelancer_conversations(self) -> List[Dict[str, Any]]:
        base_ts = int(datetime.now().timestamp())
        
        return [
            {
                'channel': 'client-updates',
                'messages': [
                    {
                        'type': 'message',
                        'user': 'U201',
                        'text': 'Hi <@U202>! Just finished implementing the shopping cart feature. You can test it at staging.yoursite.com',
                        'ts': str(base_ts - 14400)
                    },
                    {
                        'type': 'message',
                        'user': 'U202',
                        'text': 'This looks fantastic! The add-to-cart animation is really smooth. One small request - can we make the cart icon bounce when items are added?',
                        'ts': str(base_ts - 14220)
                    },
                    {
                        'type': 'message',
                        'user': 'U201',
                        'text': 'Absolutely! I\'ll add a subtle bounce animation. Should take about 30 minutes to implement',
                        'ts': str(base_ts - 14160)
                    },
                    {
                        'type': 'message',
                        'user': 'U202',
                        'text': 'Perfect! Also, my team loves the color scheme you chose. Much better than our old site :heart:',
                        'ts': str(base_ts - 14100)
                    },
                    {
                        'type': 'message',
                        'user': 'U201',
                        'text': 'Thank you! I\'ll have the cart animation ready for review this afternoon',
                        'ts': str(base_ts - 14040)
                    }
                ]
            }
        ]
    
    def _generate_individual_messages(self, scenario: str) -> List[Dict[str, Any]]:
        base_ts = int(datetime.now().timestamp())
        
        messages = [
            {
                'type': 'message',
                'user': 'U001' if scenario == 'startup' else 'U101',
                'text': 'Morning standup in 5 minutes! Please prepare your updates',
                'ts': str(base_ts - 1800),
                'channel': 'general'
            },
            {
                'type': 'message',
                'user': 'U002' if scenario == 'startup' else 'U102',
                'text': 'Code review needed on PR #42 when anyone has a chance',
                'ts': str(base_ts - 3600),
                'channel': 'dev-team'
            }
        ]
        
        return messages
    
    def format_as_documents(self, slack_data: Dict[str, Any], scenario: str = None) -> List[Dict[str, Any]]:
        documents = []
        users_map = {user['id']: user for user in slack_data.get('users', [])}
        
        for conversation in slack_data.get('conversations', []):
            conversation_text = self._build_conversation_text(conversation['messages'], users_map)
            
            doc = {
                'content': sanitize_text(conversation_text),
                'metadata': {
                    'source_type': 'slack_conversation',
                    'channel': conversation['channel'],
                    'channel_purpose': f"Demo {conversation['channel']} channel",
                    'is_private': False,
                    'message_count': len(conversation['messages']),
                    'participants': list(set(msg['user'] for msg in conversation['messages'])),
                    'start_time': conversation['messages'][0]['ts'],
                    'end_time': conversation['messages'][-1]['ts'],
                    'date': datetime.fromtimestamp(int(conversation['messages'][0]['ts'])).strftime('%Y-%m-%d'),
                    'content_hash': get_file_hash(conversation_text),
                    'file_path': f"slack/{conversation['channel']}/conv-{conversation['messages'][0]['ts']}",
                    'tags': ['slack', 'conversation', conversation['channel']],
                    'technical_terms': extract_technical_terms(conversation_text),
                    'conversation_type': self._classify_conversation_type(conversation_text),
                    'urgency': self._assess_urgency(conversation_text),
                    'summary': self._summarize_conversation(conversation, users_map),
                    'is_demo': True,
                    'demo_scenario': scenario or 'default',
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes'
                }
            }
            documents.append(doc)
        
        for message in slack_data.get('messages', []):
            if self._is_important_message(message):
                user_info = users_map.get(message['user'], {})
                clean_text = sanitize_text(message['text'])
                
                doc = {
                    'content': clean_text,
                    'metadata': {
                        'source_type': 'slack_message',
                        'channel': message.get('channel', 'unknown'),
                        'author': user_info.get('real_name', 'Unknown User'),
                        'user_id': message['user'],
                        'timestamp': message['ts'],
                        'date': datetime.fromtimestamp(int(message['ts'])).strftime('%Y-%m-%d'),
                        'is_thread': False,
                        'content_hash': get_file_hash(clean_text),
                        'file_path': f"slack/{message.get('channel', 'unknown')}/msg-{message['ts']}",
                        'tags': ['slack', 'message', message.get('channel', 'unknown')],
                        'technical_terms': extract_technical_terms(clean_text),
                        'has_code': '```' in message['text'],
                        'has_links': 'http' in message['text'],
                        'message_type': self._classify_message_type(message['text']),
                        'is_demo': True,
                        'demo_scenario': scenario or 'default',
                        'user_id': self.user_id,
                        'demo_note': 'This is synthetic demo data for showcase purposes'
                    }
                }
                documents.append(doc)
        
        return documents
    
    def _build_conversation_text(self, messages: List[Dict], users_map: Dict) -> str:
        lines = []
        
        for message in messages:
            user_info = users_map.get(message['user'], {})
            username = user_info.get('real_name', 'Unknown User')
            timestamp = datetime.fromtimestamp(int(message['ts'])).strftime('%H:%M')
            text = self._clean_message_text(message['text'])
            
            lines.append(f"[{timestamp}] {username}: {text}")
        
        return '\n'.join(lines)
    
    def _clean_message_text(self, text: str) -> str:
        import re
        
        text = re.sub(r'<@([A-Z0-9]+)>', r'@user', text)
        text = re.sub(r'<#([A-Z0-9]+)\|([^>]+)>', r'#\2', text)
        text = re.sub(r'<([^|>]+)\|([^>]+)>', r'\2 (\1)', text)
        text = re.sub(r'<([^>]+)>', r'\1', text)
        text = re.sub(r':([a-z_]+):', r'[\1]', text)
        
        return text.strip()
    
    def _classify_conversation_type(self, conversation_text: str) -> str:
        text_lower = conversation_text.lower()
        
        if any(word in text_lower for word in ['alert', 'error', 'issue', 'problem']):
            return 'incident_response'
        elif any(word in text_lower for word in ['deploy', 'release', 'production']):
            return 'deployment'
        elif any(word in text_lower for word in ['review', 'feedback', 'architecture']):
            return 'technical_review'
        elif any(word in text_lower for word in ['standup', 'meeting', 'sync']):
            return 'coordination'
        elif any(word in text_lower for word in ['client', 'customer']):
            return 'client_communication'
        else:
            return 'general_discussion'
    
    def _assess_urgency(self, conversation_text: str) -> str:
        text_lower = conversation_text.lower()
        
        if any(word in text_lower for word in ['alert', 'urgent', 'critical', 'emergency']):
            return 'high'
        elif any(word in text_lower for word in ['important', 'asap', 'priority']):
            return 'medium'
        else:
            return 'low'
    
    def _summarize_conversation(self, conversation: Dict, users_map: Dict) -> str:
        participants = set()
        for message in conversation['messages']:
            user_info = users_map.get(message['user'], {})
            username = user_info.get('real_name', 'team member')
            participants.add(username)
        
        channel = conversation['channel']
        participant_count = len(participants)
        
        return f"Team discussion in #{channel} between {participant_count} members"
    
    def _is_important_message(self, message: Dict) -> bool:
        text = message.get('text', '')
        
        if len(text) > 150:
            return True
        if '```' in text:
            return True
        if any(word in text.lower() for word in ['important', 'urgent', 'alert', 'critical']):
            return True
        
        return False
    
    def _classify_message_type(self, text: str) -> str:
        text_lower = text.lower()
        
        if '```' in text:
            return 'code_share'
        elif any(word in text_lower for word in ['solution', 'fix', 'resolved']):
            return 'solution'
        elif text.endswith('?'):
            return 'question'
        elif 'http' in text_lower:
            return 'link_share'
        else:
            return 'discussion'
    
    def get_workspace_stats(self, scenario: str = None) -> Dict[str, Any]:
        scenario = scenario or 'startup'
        slack_data = self.generate_workspace_data(scenario)
        
        return {
            'workspace_info': slack_data['workspace'],
            'users_count': len(slack_data['users']),
            'channels_count': len(slack_data['channels']),
            'conversations_count': len(slack_data['conversations']),
            'messages_count': len(slack_data['messages']),
            'total_documents': len(slack_data['conversations']) + len(slack_data['messages'])
        }


def generate_slack_demo_quick(scenario: str = 'startup', user_id: str = None) -> Dict[str, Any]:
    demo_slack = DemoSlack(user_id=user_id)
    return demo_slack.generate_workspace_data(scenario)

if __name__ == "__main__":
    import sys
    import json
    
    def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            demo_slack = DemoSlack()
            
            if command == "generate":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                data = demo_slack.generate_workspace_data(scenario)
                
                print(f"Generated Slack demo data for {scenario} scenario:")
                print(f"  Users: {len(data['users'])}")
                print(f"  Channels: {len(data['channels'])}")
                print(f"  Conversations: {len(data['conversations'])}")
                print(f"  Messages: {len(data['messages'])}")
                
            elif command == "stats":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                stats = demo_slack.get_workspace_stats(scenario)
                print("Slack Demo Statistics:")
                print(json.dumps(stats, indent=2))
                
            elif command == "documents":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                slack_data = demo_slack.generate_workspace_data(scenario)
                documents = demo_slack.format_as_documents(slack_data, scenario)
                
                print(f"Generated {len(documents)} document objects:")
                for i, doc in enumerate(documents[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"  Type: {doc['metadata']['source_type']}")
                    print(f"  Channel: {doc['metadata'].get('channel')}")
                    print(f"  Content: {doc['content'][:100]}...")
                    
            else:
                print("Available commands:")
                print("  generate [scenario] - Generate Slack demo data")
                print("  stats [scenario] - Show workspace statistics") 
                print("  documents [scenario] - Generate formatted documents")
        else:
            print("Usage: python demo_slack.py [generate|stats|documents] [scenario]")
            print("Scenarios: startup, enterprise, freelancer")
    
    main()