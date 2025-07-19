import os
import yaml
import shutil
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger
from datetime import datetime
from vector_store.chromadb_setup import ChromaDBSetup
from database.models import User, Organization
import sqlite3

class TenantManager:
    """
    Tenant Manager: Handles multi-tenant data isolation and user management
    Manages organizations, user permissions, and data access control
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.db_path = self._get_database_path()
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_database_path(self) -> str:
        """Get the database path for user management"""
        return os.path.join(
            os.path.dirname(__file__), "..", "database", "users.db"
        )
    
    def create_organization(
        self, 
        org_name: str, 
        owner_email: str, 
        plan_type: str = "starter"
    ) -> Dict[str, Any]:
        """Create a new organization and initialize its vector store"""
        try:
            org_id = self._generate_org_id(org_name)
            
            existing_org = self._get_organization(org_id)
            if existing_org:
                return {
                    "success": False,
                    "error": f"Organization {org_name} already exists",
                    "org_id": org_id
                }
            
            org_data = {
                "org_id": org_id,
                "name": org_name,
                "owner_email": owner_email,
                "plan_type": plan_type,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "active",
                "settings": {
                    "max_users": self._get_plan_limits(plan_type)["max_users"],
                    "max_documents": self._get_plan_limits(plan_type)["max_documents"],
                    "storage_gb": self._get_plan_limits(plan_type)["storage_gb"]
                }
            }
            
            success = self._store_organization(org_data)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to store organization data"
                }
            
            vector_setup = ChromaDBSetup(org_id=org_id, user_id="system")
            vector_setup.initialize_client()
            vector_setup.setup_collections()
            
            logger.info(f"Created organization: {org_name} ({org_id})")
            
            return {
                "success": True,
                "org_id": org_id,
                "org_name": org_name,
                "owner_email": owner_email,
                "plan_type": plan_type,
                "created_at": org_data["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Error creating organization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_user_to_organization(
        self,
        org_id: str,
        user_email: str,
        role: str = "member",
        permissions: List[str] = None
    ) -> Dict[str, Any]:
        """Add a user to an organization with specified role and permissions"""
        try:
            org = self._get_organization(org_id)
            if not org:
                return {
                    "success": False,
                    "error": f"Organization {org_id} not found"
                }
            
            user_id = self._generate_user_id(user_email)
            
            existing_user = self._get_user(user_id)
            if existing_user and existing_user.get("org_id") == org_id:
                return {
                    "success": False,
                    "error": f"User {user_email} already exists in organization"
                }
            
            if not permissions:
                permissions = self._get_default_permissions(role)
            
            current_users = self._get_organization_users(org_id)
            max_users = org.get("settings", {}).get("max_users", 10)
            
            if len(current_users) >= max_users:
                return {
                    "success": False,
                    "error": f"Organization has reached maximum user limit ({max_users})"
                }
            
            user_data = {
                "user_id": user_id,
                "email": user_email,
                "org_id": org_id,
                "role": role,
                "permissions": permissions,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "active"
            }
            
            success = self._store_user(user_data)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to store user data"
                }
            
            logger.info(f"Added user {user_email} to organization {org_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "email": user_email,
                "org_id": org_id,
                "role": role,
                "permissions": permissions
            }
            
        except Exception as e:
            logger.error(f"Error adding user to organization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def remove_user_from_organization(self, user_id: str, org_id: str) -> Dict[str, Any]:
        """Remove a user from an organization and clean up their data"""
        try:
            user = self._get_user(user_id)
            if not user or user.get("org_id") != org_id:
                return {
                    "success": False,
                    "error": f"User {user_id} not found in organization {org_id}"
                }
            
            user_vector_setup = ChromaDBSetup(org_id=org_id, user_id=user_id)
            user_vector_setup.initialize_client()
            
            cleanup_success = self._cleanup_user_data(user_id, org_id)
            
            delete_success = self._delete_user(user_id)
            
            logger.info(f"Removed user {user_id} from organization {org_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "org_id": org_id,
                "data_cleanup": cleanup_success,
                "user_deleted": delete_success
            }
            
        except Exception as e:
            logger.error(f"Error removing user from organization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_organization(self, org_id: str) -> Dict[str, Any]:
        """Delete an organization and all associated data"""
        try:
            org = self._get_organization(org_id)
            if not org:
                return {
                    "success": False,
                    "error": f"Organization {org_id} not found"
                }
            
            users = self._get_organization_users(org_id)
            
            for user in users:
                self.remove_user_from_organization(user["user_id"], org_id)
            
            vector_setup = ChromaDBSetup(org_id=org_id, user_id="system")
            vector_setup.initialize_client()
            vector_setup.delete_all_collections()
            
            vector_db_path = os.path.join(
                os.path.dirname(__file__), "chroma_db", org_id
            )
            if os.path.exists(vector_db_path):
                shutil.rmtree(vector_db_path)
            
            delete_success = self._delete_organization(org_id)
            
            logger.info(f"Deleted organization {org_id}")
            
            return {
                "success": True,
                "org_id": org_id,
                "users_removed": len(users),
                "org_deleted": delete_success
            }
            
        except Exception as e:
            logger.error(f"Error deleting organization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_user_permissions(
        self, 
        user_id: str, 
        required_permission: str,
        resource_type: str = None
    ) -> Dict[str, Any]:
        """Check if a user has the required permission"""
        try:
            user = self._get_user(user_id)
            if not user:
                return {
                    "has_permission": False,
                    "error": f"User {user_id} not found"
                }
            
            if user.get("status") != "active":
                return {
                    "has_permission": False,
                    "error": "User account is not active"
                }
            
            user_permissions = user.get("permissions", [])
            user_role = user.get("role", "member")
            
            has_permission = (
                required_permission in user_permissions or
                user_role == "admin" or
                (user_role == "owner" and required_permission != "delete_org")
            )
            
            return {
                "has_permission": has_permission,
                "user_id": user_id,
                "role": user_role,
                "permissions": user_permissions,
                "checked_permission": required_permission
            }
            
        except Exception as e:
            logger.error(f"Error checking user permissions: {str(e)}")
            return {
                "has_permission": False,
                "error": str(e)
            }
    
    def get_user_organizations(self, user_email: str) -> Dict[str, Any]:
        """Get all organizations a user belongs to"""
        try:
            user_id = self._generate_user_id(user_email)
            user = self._get_user(user_id)
            
            if not user:
                return {
                    "success": True,
                    "organizations": [],
                    "count": 0
                }
            
            org = self._get_organization(user["org_id"])
            
            organizations = []
            if org:
                organizations.append({
                    "org_id": org["org_id"],
                    "name": org["name"],
                    "role": user["role"],
                    "joined_at": user["created_at"],
                    "status": user["status"]
                })
            
            return {
                "success": True,
                "organizations": organizations,
                "count": len(organizations)
            }
            
        except Exception as e:
            logger.error(f"Error getting user organizations: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "organizations": [],
                "count": 0
            }
    
    def get_organization_usage(self, org_id: str) -> Dict[str, Any]:
        """Get organization usage statistics"""
        try:
            org = self._get_organization(org_id)
            if not org:
                return {
                    "success": False,
                    "error": f"Organization {org_id} not found"
                }
            
            users = self._get_organization_users(org_id)
            user_count = len(users)
            
            vector_setup = ChromaDBSetup(org_id=org_id, user_id="system")
            vector_setup.initialize_client()
            stats = vector_setup.get_collection_stats()
            
            total_documents = sum(
                collection.get("count", 0) 
                for collection in stats.values() 
                if isinstance(collection, dict)
            )
            
            limits = org.get("settings", {})
            
            usage = {
                "org_id": org_id,
                "org_name": org.get("name"),
                "plan_type": org.get("plan_type"),
                "current_usage": {
                    "users": user_count,
                    "documents": total_documents,
                    "collections": len(stats)
                },
                "limits": {
                    "max_users": limits.get("max_users", 10),
                    "max_documents": limits.get("max_documents", 10000),
                    "storage_gb": limits.get("storage_gb", 5)
                },
                "usage_percentage": {
                    "users": round((user_count / limits.get("max_users", 10)) * 100, 1),
                    "documents": round((total_documents / limits.get("max_documents", 10000)) * 100, 1)
                }
            }
            
            return {
                "success": True,
                "usage": usage
            }
            
        except Exception as e:
            logger.error(f"Error getting organization usage: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def migrate_user_data(
        self, 
        user_id: str, 
        from_org_id: str, 
        to_org_id: str
    ) -> Dict[str, Any]:
        """Migrate user data from one organization to another"""
        try:
            user = self._get_user(user_id)
            if not user or user.get("org_id") != from_org_id:
                return {
                    "success": False,
                    "error": f"User {user_id} not found in source organization"
                }
            
            to_org = self._get_organization(to_org_id)
            if not to_org:
                return {
                    "success": False,
                    "error": f"Target organization {to_org_id} not found"
                }
            
            user["org_id"] = to_org_id
            user["migrated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            success = self._store_user(user)
            
            logger.info(f"Migrated user {user_id} from {from_org_id} to {to_org_id}")
            
            return {
                "success": success,
                "user_id": user_id,
                "from_org_id": from_org_id,
                "to_org_id": to_org_id,
                "migrated_at": user["migrated_at"]
            }
            
        except Exception as e:
            logger.error(f"Error migrating user data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_org_id(self, org_name: str) -> str:
        """Generate unique organization ID"""
        import re
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', org_name.lower())
        timestamp = datetime.now().strftime("%m%d")
        return f"{clean_name}_{timestamp}"
    
    def _generate_user_id(self, email: str) -> str:
        """Generate unique user ID from email"""
        import hashlib
        return hashlib.md5(email.lower().encode()).hexdigest()[:12]
    
    def _get_plan_limits(self, plan_type: str) -> Dict[str, int]:
        """Get resource limits for plan type"""
        limits = {
            "starter": {"max_users": 5, "max_documents": 5000, "storage_gb": 2},
            "professional": {"max_users": 25, "max_documents": 50000, "storage_gb": 10},
            "enterprise": {"max_users": 100, "max_documents": 500000, "storage_gb": 100},
            "demo": {"max_users": 1, "max_documents": 1000, "storage_gb": 1}
        }
        return limits.get(plan_type, limits["starter"])
    
    def _get_default_permissions(self, role: str) -> List[str]:
        """Get default permissions for role"""
        permissions = {
            "owner": ["read", "write", "delete", "manage_users", "manage_org"],
            "admin": ["read", "write", "delete", "manage_users"],
            "editor": ["read", "write"],
            "member": ["read"],
            "viewer": ["read"]
        }
        return permissions.get(role, permissions["member"])
    
    def _cleanup_user_data(self, user_id: str, org_id: str) -> bool:
        """Clean up user-specific data from vector store"""
        try:
            vector_setup = ChromaDBSetup(org_id=org_id, user_id=user_id)
            vector_setup.initialize_client()
            
            for collection_name, collection in vector_setup.collections.items():
                try:
                    user_docs = collection.get(
                        where={"user_id": user_id},
                        include=["ids"]
                    )
                    
                    if user_docs.get("ids"):
                        collection.delete(ids=user_docs["ids"])
                        logger.debug(f"Cleaned {len(user_docs['ids'])} documents for user {user_id}")
                
                except Exception as e:
                    logger.warning(f"Error cleaning collection {collection_name}: {str(e)}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning user data: {str(e)}")
            return False
    
    def _get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM organizations WHERE org_id = ?",
                (org_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                org_data = dict(row)
                if org_data.get("settings"):
                    import json
                    org_data["settings"] = json.loads(org_data["settings"])
                return org_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting organization: {str(e)}")
            return None
    
    def _store_organization(self, org_data: Dict[str, Any]) -> bool:
        """Store organization data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            import json
            settings_json = json.dumps(org_data.get("settings", {}))
            
            cursor.execute("""
                INSERT OR REPLACE INTO organizations 
                (org_id, name, owner_email, plan_type, created_at, status, settings)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                org_data["org_id"],
                org_data["name"],
                org_data["owner_email"],
                org_data["plan_type"],
                org_data["created_at"],
                org_data["status"],
                settings_json
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error storing organization: {str(e)}")
            return False
    
    def _get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user_data = dict(row)
                if user_data.get("permissions"):
                    import json
                    user_data["permissions"] = json.loads(user_data["permissions"])
                return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
    
    def _store_user(self, user_data: Dict[str, Any]) -> bool:
        """Store user data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            import json
            permissions_json = json.dumps(user_data.get("permissions", []))
            
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, email, org_id, role, permissions, created_at, last_active, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data["user_id"],
                user_data["email"],
                user_data["org_id"],
                user_data["role"],
                permissions_json,
                user_data["created_at"],
                user_data["last_active"],
                user_data["status"]
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error storing user: {str(e)}")
            return False
    
    def _get_organization_users(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all users in an organization"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM users WHERE org_id = ? AND status = 'active'",
                (org_id,)
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                user_data = dict(row)
                if user_data.get("permissions"):
                    import json
                    user_data["permissions"] = json.loads(user_data["permissions"])
                users.append(user_data)
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting organization users: {str(e)}")
            return []
    
    def _delete_user(self, user_id: str) -> bool:
        """Delete user from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
    
    def _delete_organization(self, org_id: str) -> bool:
        """Delete organization from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM organizations WHERE org_id = ?", (org_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting organization: {str(e)}")
            return False

def create_demo_tenant() -> Dict[str, Any]:
    """Create demo tenant for showcasing"""
    manager = TenantManager()
    return manager.create_organization(
        org_name="Demo Company",
        owner_email="demo@example.com",
        plan_type="demo"
    )

def setup_user_tenant(org_name: str, owner_email: str, plan_type: str = "starter") -> Dict[str, Any]:
    """Quick setup for new organization"""
    manager = TenantManager()
    return manager.create_organization(org_name, owner_email, plan_type)

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        manager = TenantManager()
        
        if command == "create_org":
            org_name = sys.argv[2] if len(sys.argv) > 2 else "Test Org"
            owner_email = sys.argv[3] if len(sys.argv) > 3 else "test@example.com"
            result = manager.create_organization(org_name, owner_email)
            print(json.dumps(result, indent=2))
            
        elif command == "add_user":
            org_id = sys.argv[2] if len(sys.argv) > 2 else ""
            user_email = sys.argv[3] if len(sys.argv) > 3 else ""
            role = sys.argv[4] if len(sys.argv) > 4 else "member"
            result = manager.add_user_to_organization(org_id, user_email, role)
            print(json.dumps(result, indent=2))
            
        elif command == "usage":
            org_id = sys.argv[2] if len(sys.argv) > 2 else ""
            result = manager.get_organization_usage(org_id)
            print(json.dumps(result, indent=2))
            
        elif command == "demo":
            result = create_demo_tenant()
            print(json.dumps(result, indent=2))
            
        else:
            print("Available commands:")
            print("  create_org [name] [owner_email] - Create organization")
            print("  add_user [org_id] [email] [role] - Add user to organization")
            print("  usage [org_id] - Show organization usage")
            print("  demo - Create demo tenant")
    else:
        print("Usage: python tenant_manager.py [create_org|add_user|usage|demo] [args...]")