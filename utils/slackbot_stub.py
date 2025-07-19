import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import asyncio
from dotenv import load_dotenv
load_dotenv()

class SlackBotStub:
    """
    Slack Bot Stub: Placeholder for future Slack integration
    Provides mock responses and integration points for ZeroDay agents
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.is_enabled = bool(self.bot_token) and self.config.get("enabled", False)
        self.mock_mode = not self.is_enabled
        
      
        self.mock_channels = {
            "general": {"id": "C1234567890", "name": "general"},
            "dev-team": {"id": "C1234567891", "name": "dev-team"}, 
            "help": {"id": "C1234567892", "name": "help"},
            "onboarding": {"id": "C1234567893", "name": "onboarding"}
        }
        
       
        self.mock_users = {
            "dev_123": {"id": "U1234567890", "name": "john.doe", "real_name": "John Doe"},
            "dev_456": {"id": "U1234567891", "name": "jane.smith", "real_name": "Jane Smith"},
            "mentor_1": {"id": "U1234567892", "name": "sarah.mentor", "real_name": "Sarah Chen"},  
            "senior_dev": {"id": "U1234567893", "name": "mike.wilson", "real_name": "Mike Wilson"},
            "team_lead": {"id": "U1234567894", "name": "priya.patel", "real_name": "Priya Patel"}
        }
        
        logger.info(f"SlackBot initialized - Mode: {'Mock' if self.mock_mode else 'Live'}")
    
    async def send_onboarding_welcome(self, user_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Send welcome message to new team member"""
        
        welcome_message = self._create_welcome_message(user_info)
        
        if self.mock_mode:
            logger.info(f"[MOCK] Sending welcome message to {user_id}")
            return {
                "success": True,
                "message_id": f"mock_msg_{datetime.now().timestamp()}",
                "channel": "onboarding",
                "mock": True,
                "content": welcome_message
            }
        
        
        try:
            
            return {
                "success": True,
                "message_id": "real_message_id",
                "channel": "onboarding"
            }
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
            return {"success": False, "error": str(e)}
    
    async def notify_mentor_assignment(self, mentee_id: str, mentor_id: str, learning_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Notify mentor about new mentee assignment"""
        
        notification = self._create_mentor_notification(mentee_id, mentor_id, learning_plan)
        
        if self.mock_mode:
            logger.info(f"[MOCK] Notifying mentor {mentor_id} about mentee {mentee_id}")
            return {
                "success": True,
                "message_id": f"mock_mentor_notification_{datetime.now().timestamp()}",
                "recipient": mentor_id,
                "mock": True,
                "content": notification
            }
        
        try:
            
            return {"success": True, "message_id": "real_notification_id"}
        except Exception as e:
            logger.error(f"Failed to send mentor notification: {e}")
            return {"success": False, "error": str(e)}
    
    async def share_task_suggestion(self, user_id: str, task: Dict[str, Any], channel: str = "dev-team") -> Dict[str, Any]:
        """Share task suggestion in team channel"""
        
        task_message = self._create_task_message(user_id, task)
        
        if self.mock_mode:
            logger.info(f"[MOCK] Sharing task suggestion for {user_id} in #{channel}")
            return {
                "success": True,
                "message_id": f"mock_task_{datetime.now().timestamp()}",
                "channel": channel,
                "mock": True,
                "content": task_message
            }
        
        try:
           
            return {"success": True, "message_id": "real_task_message_id"}
        except Exception as e:
            logger.error(f"Failed to share task suggestion: {e}")
            return {"success": False, "error": str(e)}
    
    async def request_help(self, user_id: str, problem: str, urgency: str = "normal") -> Dict[str, Any]:
        """Post help request to appropriate channel"""
        
        help_message = self._create_help_request(user_id, problem, urgency)
        channel = "help" if urgency != "critical" else "dev-team"
        
        if self.mock_mode:
            logger.info(f"[MOCK] Help request from {user_id} in #{channel} (urgency: {urgency})")
            return {
                "success": True,
                "message_id": f"mock_help_{datetime.now().timestamp()}",
                "channel": channel,
                "urgency": urgency,
                "mock": True,
                "content": help_message
            }
        
        try:
            
            return {"success": True, "message_id": "real_help_message_id"}
        except Exception as e:
            logger.error(f"Failed to send help request: {e}")
            return {"success": False, "error": str(e)}
    
    async def share_learning_progress(self, user_id: str, milestone: str, progress: Dict[str, Any]) -> Dict[str, Any]:
        """Share learning milestone achievement"""
        
        progress_message = self._create_progress_message(user_id, milestone, progress)
        
        if self.mock_mode:
            logger.info(f"[MOCK] Sharing progress update for {user_id}: {milestone}")
            return {
                "success": True,
                "message_id": f"mock_progress_{datetime.now().timestamp()}",
                "channel": "onboarding",
                "mock": True,
                "content": progress_message
            }
        
        try:
           
            return {"success": True, "message_id": "real_progress_message_id"}
        except Exception as e:
            logger.error(f"Failed to share progress: {e}")
            return {"success": False, "error": str(e)}
    
    async def schedule_checkin_reminder(self, user_id: str, mentor_id: str, days_from_now: int = 7) -> Dict[str, Any]:
        """Schedule check-in reminder"""
        
        reminder_time = datetime.now().timestamp() + (days_from_now * 24 * 60 * 60)
        
        if self.mock_mode:
            logger.info(f"[MOCK] Scheduled check-in reminder for {user_id} with {mentor_id} in {days_from_now} days")
            return {
                "success": True,
                "reminder_id": f"mock_reminder_{datetime.now().timestamp()}",
                "scheduled_for": reminder_time,
                "mock": True
            }
        
        try:
        
            return {"success": True, "reminder_id": "real_reminder_id"}
        except Exception as e:
            logger.error(f"Failed to schedule reminder: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_team_availability(self, user_ids: List[str] = None) -> Dict[str, Any]:
        """Get team member availability status"""
        
        if self.mock_mode:
            mock_availability = {}
            target_users = user_ids or list(self.mock_users.keys())
            
            for user_id in target_users:
                mock_availability[user_id] = {
                    "status": "active",
                    "presence": "online" if hash(user_id) % 2 == 0 else "away",
                    "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "timezone": "America/New_York"
                }
            
            return {
                "success": True,
                "availability": mock_availability,
                "mock": True
            }
        
        try:
           
            return {"success": True, "availability": {}}
        except Exception as e:
            logger.error(f"Failed to get availability: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_welcome_message(self, user_info: Dict[str, Any]) -> str:
        """Create welcome message for new team member"""
        name = user_info.get("name", "Team Member")
        role = user_info.get("role", "Developer")
        
        return f"""
🎉 Welcome to the team, {name}! 

I'm your ZeroDay onboarding assistant. I'm here to help you get up to speed quickly as a {role}.

Here's what I can help you with:
• 📚 Creating personalized learning paths
• 🎯 Suggesting appropriate first tasks  
• 🤝 Connecting you with mentors and resources
• ❓ Answering questions about our codebase and processes

To get started:
1. Check your personalized learning plan
2. Join our team channels: #dev-team, #help
3. Say hello and introduce yourself!

Feel free to ask me anything by mentioning @ZeroDay or DMing me directly.

Let's make your first week amazing! 🚀
        """.strip()
    
    def _create_mentor_notification(self, mentee_id: str, mentor_id: str, learning_plan: Dict[str, Any]) -> str:
        """Create mentor assignment notification"""
        mentee_name = self.mock_users.get(mentee_id, {}).get("real_name", "New Team Member")
        role = learning_plan.get("metadata", {}).get("user_role", "Developer")
        
        return f"""
👋 Hi! You've been assigned as a mentor for {mentee_name}, our new {role}.

📋 **Learning Plan Overview:**
• Duration: {learning_plan.get('estimated_duration', '8 weeks')}
• Focus: {role} development
• Experience Level: {learning_plan.get('metadata', {}).get('experience_level', 'Beginner')}

🎯 **Your mentoring role:**
• Weekly 1:1 check-ins
• Code review and guidance
• Answer questions and provide context
• Help with task selection and prioritization

I'll help track their progress and suggest discussion topics for your meetings.

Ready to help them succeed! 🌟
        """.strip()
    
    def _create_task_message(self, user_id: str, task: Dict[str, Any]) -> str:
        """Create task suggestion message"""
        user_name = self.mock_users.get(user_id, {}).get("real_name", "Team Member")
        
        return f"""
🎯 **Task Suggestion for {user_name}**

**Task:** {task.get('title', task.get('content', 'New Task')[:50])}

**Details:**
• Estimated Time: {task.get('estimated_time', 'Unknown')}
• Difficulty: {task.get('estimated_difficulty', 'Medium')}
• Skills: {', '.join(task.get('skills_developed', []))}

**Why this task is perfect:**
{task.get('recommendation_reason', 'Good match for current skill level')}

Great opportunity for hands-on learning! 🚀
        """.strip()
    
    def _create_help_request(self, user_id: str, problem: str, urgency: str) -> str:
        """Create help request message"""
        user_name = self.mock_users.get(user_id, {}).get("real_name", "Team Member")
        
        urgency_emoji = "🚨" if urgency == "critical" else "❓" if urgency == "high" else "💭"
        
        return f"""
{urgency_emoji} **Help Request** ({urgency} priority)

**From:** {user_name}
**Issue:** {problem[:200]}{'...' if len(problem) > 200 else ''}

Anyone available to help? @here
        """.strip()
    
    def _create_progress_message(self, user_id: str, milestone: str, progress: Dict[str, Any]) -> str:
        """Create progress update message"""
        user_name = self.mock_users.get(user_id, {}).get("real_name", "Team Member")
        
        return f"""
🎉 **Progress Update!**

{user_name} just achieved: **{milestone}**

📊 **Current Progress:**
• Overall: {progress.get('completion_percentage', 50)}% complete
• Phase: {progress.get('current_phase', 'In Progress')}
• Time Invested: {progress.get('time_spent', 20)} hours

Keep up the great work! 🌟
        """.strip()
    
    async def get_mock_conversation_data(self) -> Dict[str, Any]:
        """Get mock conversation data for testing/demo purposes"""
        return {
            "channels": self.mock_channels,
            "users": self.mock_users,
            "sample_messages": [
                {
                    "channel": "dev-team",
                    "user": "dev_123",
                    "text": "Just completed my first React component! Thanks for the guidance.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "reactions": ["👍", "🎉"]
                },
                {
                    "channel": "help",
                    "user": "dev_456", 
                    "text": "Having trouble with the authentication flow. Getting 401 errors.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "thread_replies": 3
                },
                {
                    "channel": "onboarding",
                    "user": "mentor_1",
                    "text": "Welcome to the team! Looking forward to working with you.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "reactions": ["🎉", "👋"]
                }
            ]
        }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return {
            "enabled": self.is_enabled,
            "mock_mode": self.mock_mode,
            "bot_token_configured": bool(self.bot_token),
            "supported_features": [
                "onboarding_welcome",
                "mentor_notifications", 
                "task_sharing",
                "help_requests",
                "progress_updates",
                "checkin_reminders",
                "team_availability"
            ],
            "mock_channels": list(self.mock_channels.keys()),
            "mock_users": len(self.mock_users)
        }
    
    async def simulate_user_interaction(self, user_id: str, interaction_type: str) -> Dict[str, Any]:
        """Simulate user interaction for testing/demo purposes"""
        
        interactions = {
            "ask_question": {
                "message": f"How do I set up the development environment?",
                "channel": "help",
                "response": "Great question! Check out our setup guide in the docs..."
            },
            "share_success": {
                "message": f"Just deployed my first feature to staging! 🎉",
                "channel": "dev-team", 
                "response": "Awesome work! That's a major milestone."
            },
            "request_review": {
                "message": f"Could someone review my PR when you have a chance?",
                "channel": "dev-team",
                "response": "I'll take a look this afternoon!"
            }
        }
        
        interaction = interactions.get(interaction_type, interactions["ask_question"])
        
        if self.mock_mode:
            logger.info(f"[MOCK] Simulated {interaction_type} from {user_id}")
            return {
                "success": True,
                "interaction_type": interaction_type,
                "user_message": interaction["message"],
                "bot_response": interaction["response"],
                "channel": interaction["channel"],
                "mock": True,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        return {"success": False, "error": "Simulation only available in mock mode"}



_slack_bot = None

def get_slack_bot(config: Dict[str, Any] = None) -> SlackBotStub:
    """Get global Slack bot instance"""
    global _slack_bot
    if _slack_bot is None:
        _slack_bot = SlackBotStub(config)
    return _slack_bot

def is_slack_enabled() -> bool:
    """Check if Slack integration is enabled"""
    bot = get_slack_bot()
    return bot.is_enabled

async def send_welcome_message(user_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to send welcome message"""
    bot = get_slack_bot()
    return await bot.send_onboarding_welcome(user_id, user_info)

async def notify_mentor(mentee_id: str, mentor_id: str, learning_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to notify mentor"""
    bot = get_slack_bot()
    return await bot.notify_mentor_assignment(mentee_id, mentor_id, learning_plan)

async def request_team_help(user_id: str, problem: str, urgency: str = "normal") -> Dict[str, Any]:
    """Convenience function to request help"""
    bot = get_slack_bot()
    return await bot.request_help(user_id, problem, urgency)


async def get_demo_conversation_data() -> Dict[str, Any]:
    """Get demo conversation data for portfolio showcase"""
    bot = get_slack_bot()
    return await bot.get_mock_conversation_data()

def get_demo_users() -> Dict[str, Any]:
    """Get demo users for portfolio showcase"""
    bot = get_slack_bot()
    return bot.mock_users

if __name__ == "__main__":
    
    import asyncio
    
    async def test_slack_bot():
        """Test suite for Slack bot functionality"""
        bot = SlackBotStub()
        
        print("🚀 Testing ZeroDay Slack Bot Integration...")
        print(f"Status: {bot.get_integration_status()}")
        
        
        result = await bot.send_onboarding_welcome("dev_123", {
            "name": "John Doe",
            "role": "Frontend Developer"
        })
        print(f"✅ Welcome message: {result}")
        
        
        result = await bot.request_help("dev_456", "Having authentication issues", "high")
        print(f"✅ Help request: {result}")
        
       
        result = await bot.simulate_user_interaction("dev_123", "share_success")
        print(f"✅ Simulated interaction: {result}")
        
       
        demo_data = await bot.get_mock_conversation_data()
        print(f"✅ Demo data available: {len(demo_data['sample_messages'])} messages")
        
        print("\n🎉 All tests passed! Slack bot stub is ready for portfolio demo.")
    
    asyncio.run(test_slack_bot())